"""CLI: pathladder --schema barretts_ladder --input reports.csv --text-col text --out labels.csv"""
import argparse, sys
import pandas as pd
from . import BARRETTS_LADDER, TCGA_GI, label_frame

SCHEMAS = {"barretts_ladder": BARRETTS_LADDER, "tcga_gi": TCGA_GI}


def main(argv=None):
    p = argparse.ArgumentParser(prog="pathladder",
                                description="Extract weak labels from pathology report text.")
    p.add_argument("--schema", choices=sorted(SCHEMAS), required=True)
    p.add_argument("--input", required=True, help="CSV (or .csv.gz) of reports")
    p.add_argument("--text-col", required=True)
    p.add_argument("--id-col", default=None, help="carried through to output if given")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)

    df = pd.read_csv(a.input)
    if a.text_col not in df.columns:
        sys.exit(f"column {a.text_col!r} not in {list(df.columns)}")
    labels = label_frame(df, a.text_col, SCHEMAS[a.schema])
    if a.id_col:
        labels.insert(0, a.id_col, df[a.id_col].values)
    labels.to_csv(a.out, index=False)
    counts = {c: labels[c].value_counts(dropna=False).to_dict() for c in labels.columns if c != a.id_col}
    print(f"wrote {a.out} ({len(labels)} rows)")
    for c, d in counts.items():
        print(f"  {c}: {d}")


if __name__ == "__main__":
    main()
