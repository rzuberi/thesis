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
