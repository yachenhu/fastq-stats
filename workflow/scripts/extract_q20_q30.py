#!/usr/bin/env python3
"""
Extract Q20 and Q30 statistics from fastp JSON output.

This script parses fastp JSON files and extracts the percentage of bases
with quality scores >= 20 (Q20) and >= 30 (Q30) for both R1 and R2 reads.
"""

import json
import sys
import pandas as pd


def extract_q20_q30(json_file):
    """
    Extract Q20 and Q30 percentages from fastp JSON output.

    Args:
        json_file: Path to fastp JSON output file

    Returns:
        Dictionary containing Q20/Q30 statistics for R1 and R2
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract quality metrics for R1 and R2
    r1_quality = data['summary']['before_filtering']['read1_quality']
    r2_quality = data['summary']['before_filtering']['read2_quality']

    # Get Q20 and Q30 percentages (these are typically in the quality_curves section)
    # Fastp provides quality distributions, we need to calculate Q20/Q30 from the data

    # Extract quality distribution data
    r1_qual_dist = data['quality_curves']['read1_quality_curve']
    r2_qual_dist = data['quality_curves']['read2_quality_curve']

    # Calculate Q20 and Q30 percentages
    # Q20: bases with quality score >= 20
    # Q30: bases with quality score >= 30

    def calculate_q_percentage(qual_dist, threshold):
        """Calculate percentage of bases above quality threshold."""
        total_bases = sum(qual_dist.values())
        if total_bases == 0:
            return 0.0

        above_threshold = sum(count for quality, count in qual_dist.items()
                            if quality >= threshold)
        return (above_threshold / total_bases) * 100

    r1_q20 = calculate_q_percentage(r1_qual_dist, 20)
    r1_q30 = calculate_q_percentage(r1_qual_dist, 30)
    r2_q20 = calculate_q_percentage(r2_qual_dist, 20)
    r2_q30 = calculate_q_percentage(r2_qual_dist, 30)

    # Get overall quality statistics
    r1_mean_qual = data['summary']['before_filtering']['read1_mean_quality']
    r2_mean_qual = data['summary']['before_filtering']['read2_mean_quality']

    # Get total bases and reads
    r1_total_bases = data['summary']['before_filtering']['read1_total_bases']
    r2_total_bases = data['summary']['before_filtering']['read2_total_bases']
    r1_total_reads = data['summary']['before_filtering']['read1_total_reads']
    r2_total_reads = data['summary']['before_filtering']['read2_total_reads']

    return {
        'sample': data['summary']['before_filtering'].get('sample', 'unknown'),
        'r1_q20_percent': round(r1_q20, 2),
        'r1_q30_percent': round(r1_q30, 2),
        'r1_mean_quality': round(r1_mean_qual, 2),
        'r1_total_bases': r1_total_bases,
        'r1_total_reads': r1_total_reads,
        'r2_q20_percent': round(r2_q20, 2),
        'r2_q30_percent': round(r2_q30, 2),
        'r2_mean_quality': round(r2_mean_qual, 2),
        'r2_total_bases': r2_total_bases,
        'r2_total_reads': r2_total_reads,
        'overall_q20_percent': round((r1_q20 * r1_total_bases + r2_q20 * r2_total_bases) /
                                    (r1_total_bases + r2_total_bases), 2),
        'overall_q30_percent': round((r1_q30 * r1_total_bases + r2_q30 * r2_total_bases) /
                                    (r1_total_bases + r2_total_bases), 2)
    }


def main():
    # Get input and output files from Snakemake
    if len(sys.argv) == 3:
        json_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Fallback: use Snakemake workflow object if available
        try:
            json_file = snakemake.input[0]
            output_file = snakemake.output[0]
        except NameError:
            print("Usage: python extract_q20_q30.py <input.json> <output.tsv>")
            sys.exit(1)

    # Extract statistics
    stats = extract_q20_q30(json_file)

    # Create DataFrame and save as TSV
    df = pd.DataFrame([stats])
    df.to_csv(output_file, sep='\t', index=False)

    print(f"Extracted Q20/Q30 statistics from {json_file} to {output_file}")


if __name__ == '__main__':
    main()