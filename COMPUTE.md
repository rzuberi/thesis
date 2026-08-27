# Cluster compute + job-submission pattern (verified 2026-08-14)

## Partitions

| Partition | Hardware | QoS used in template | Notes |
|---|---|---|---|
| `h200` | 2 nodes × 8 × NVIDIA H200 | `h200_preempt` | preemptible — tasks must be idempotent (the race-to-run pattern handles this) |
| `cuda` | 6 nodes × 4 × L40S | `test_cuda` (short) | main CUDA workhorse for feature extraction |
| `rocm` | 9 nodes × 8 × AMD MI50 | `test_rocm` | **AMD/ROCm** — CUDA-only WSI pipelines will not run; exclude from GPU fan-outs |
| `epyc` (default) | 28 nodes, 1,792 cores | `test_epyc` | CPU — fusion first-passes on precomputed features, probes, aggregation |

## Race-to-run duplicate-submission pattern

Canonical implementation: `phd/occams_multimodal/`
- `submit_clinical_survival_5yr_all_partitions.sh` — fans each task to ALL partitions
  (one sbatch per partition, per-partition QoS/time/mem args, task grid via env vars)
- `run_clinical_survival_5yr_task.sh` — makes duplicates harmless:
  1. `done.json` exists → exit 0 (late duplicate)
  2. atomic `mkdir .lock` → first job to start wins
  3. lock held → `squeue` check on owner: alive → exit 0; dead → stale-lock reclaim
     (covers h200 preemption)
  4. winner runs task → writes `done.json` (job id, partition, host, timestamp);
     `trap` removes own lock on exit

Known benign race: two jobs in simultaneous stale-lock reclaim can both pass the
retry; harmless if tasks are idempotent and write to task-scoped output dirs.

## Job-granularity convention (Rehan's preference, 2026-08-14)
Break campaigns into the **smallest independent unit** and submit each as its own
race-to-run task (own done-marker + lock): one slide per feature-extraction task,
one file per download task, one config per training task. Benefits: maximum
parallelism across partitions, failures cost one unit, resubmission is idempotent
(done markers skip finished units). Prefer many small jobs over one long job;
use short --time per unit so the scheduler backfills them.

## Usage guidance for thesis gates
- OCCAMS H&E+genomics fusion first-pass (Ch2): epyc fan-out (features precomputed → CPU).
- ERIN + TCGA feature extraction (Ch3/Ch4/Ch2): `PARTITIONS=cuda,h200` only (CUDA
  pipelines); read WSIs from the **fast** pool copies (see DATASETS.md).
- TCGA TP53/WGD probe (Ch2 Part A): epyc, minutes.
- Monitoring helper: `~/slurm_eta_watch.sh`.

## Download throughput (measured 2026-08-20)
GDC API: 40 parallel streams from epyc sustained ~234 MB/s aggregate (305 GB in
~30 min) with 1/381 transient failure. Single-stream is ~4-6 MB/s — always
parallelise GDC pulls; the %40 array throttle did not bind. The ceiling was never
hit; raise beyond 40 only if a campaign needs it, since a rate-limit block on the
shared cluster IP stalls everyone.

## Hard-won submission rules (2026-08-27)

- **h200 is preemptible — never h200 alone.** Other groups hold priority on the
  H200 partition (QoS `h200_preempt`) and can cancel our RUNNING jobs. Every
  h200 submission must have a cuda (or epyc) twin of the same task. Workers
  must be resume-capable; after a preemption or scancel expect a STALE LOCK
  (`rm -rf feasibility/runs/<task>/.lock` before resubmitting — a killed job's
  exit trap may not fire).
- **Env × partition:** `erin` (torch 2.0.1+cu117) has no sm_90 kernels — torch
  jobs on h200 need `CONDA_ENV=virchow2` (torch 2.9.1+cu128). `erin` is fine on
  cuda/L40S. ollama jobs carry their own CUDA runtime and run anywhere.
- **Backfill:** request realistic walltimes (3h, not 12h) — short jobs slot
  into scheduler gaps; long ones queue behind Priority for a day or more.
