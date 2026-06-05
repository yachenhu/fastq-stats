#!/usr/bin/env python3
"""
Merge per-sample fastp statistics TSVs into a single consolidated table.
"""

import pandas as pd


def main():
    dfs = [pd.read_table(p) for p in snakemake.input]
    merged = pd.concat(dfs, ignore_index=True).sort_values("sample").reset_index(drop=True)
    merged.to_csv(snakemake.output[0], sep="\t", index=False)


if __name__ == "__main__":
    main()
