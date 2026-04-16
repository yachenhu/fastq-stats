#!/usr/bin/env python3
"""
Merge comprehensive fastp statistics from multiple samples into a single table.

This script takes multiple TSV files containing fastp statistics
and merges them into a single consolidated table for downstream analysis.

Statistics include over 50 metrics covering:
- Basic stats (reads, bases, GC content)
- Quality stats (Q20, Q30, mean quality)
- Filtering stats (reads filtered by category)
- Duplication rate
- Insert size metrics
- Per-read breakdown (R1 vs R2)
"""

import pandas as pd
import sys
import glob


def merge_q20_q30_files(input_files, output_file):
    """
    Merge multiple Q20/Q30 summary files into a single table.

    Args:
        input_files: List of input TSV file paths
        output_file: Path to output merged TSV file
    """
    # Read all input files
    dfs = []
    for file in input_files:
        df = pd.read_csv(file, sep='\t')
        dfs.append(df)

    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)

    # Sort by sample name
    merged_df = merged_df.sort_values('sample').reset_index(drop=True)

    # Save merged dataframe
    merged_df.to_csv(output_file, sep='\t', index=False)

    print(f"Merged {len(input_files)} fastp stats files into {output_file}")
    print(f"Total samples: {len(merged_df)}")
    print(f"Total metrics: {len(merged_df.columns)}")


def main():
    # Parse command line arguments
    if len(sys.argv) >= 3:
        # Get all input files (first argument is the script itself)
        input_files = sys.argv[1:-1]
        output_file = sys.argv[-1]
    else:
        print("Usage: python merge_q20_q30.py <input1.tsv> <input2.tsv> ... <output.tsv>")
        sys.exit(1)

    # Merge files
    merge_q20_q30_files(input_files, output_file)


if __name__ == '__main__':
    main()