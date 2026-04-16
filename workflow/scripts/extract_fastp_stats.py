#!/usr/bin/env python3
"""
Extract comprehensive statistics from fastp JSON output.

This script parses fastp JSON files and extracts a wide range of quality,
filtering, and content metrics for both R1 and R2 reads.
"""

import json
import sys
import pandas as pd
from pathlib import Path


def extract_fastp_stats(json_file):
    """
    Extract comprehensive statistics from fastp JSON output.

    Args:
        json_file: Path to fastp JSON output file

    Returns:
        Dictionary containing comprehensive statistics
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract sample name from file path if available
    sample = Path(json_file).stem

    # Extract summary statistics (before and after filtering)
    summary = data['summary']
    before = summary['before_filtering']
    after = summary['after_filtering']

    # Extract filtering results
    filtering = data['filtering_result']

    # Extract duplication metrics
    duplication = data['duplication']

    # Extract insert size metrics
    insert_size = data['insert_size']

    # Extract per-read statistics
    r1_before = data['read1_before_filtering']
    r2_before = data['read2_before_filtering']
    r1_after = data['read1_after_filtering']
    r2_after = data['read2_after_filtering']

    # Calculate Q20/Q30 rates from per-read data (more accurate than summary)
    def calc_q_rate(q_bases, total_bases):
        return round((q_bases / total_bases) * 100, 2) if total_bases > 0 else 0.0

    # R1 statistics
    r1_q20_rate = calc_q_rate(r1_before['q20_bases'], r1_before['total_bases'])
    r1_q30_rate = calc_q_rate(r1_before['q30_bases'], r1_before['total_bases'])
    r1_q20_rate_after = calc_q_rate(r1_after['q20_bases'], r1_after['total_bases'])
    r1_q30_rate_after = calc_q_rate(r1_after['q30_bases'], r1_after['total_bases'])

    # R2 statistics
    r2_q20_rate = calc_q_rate(r2_before['q20_bases'], r2_before['total_bases'])
    r2_q30_rate = calc_q_rate(r2_before['q30_bases'], r2_before['total_bases'])
    r2_q20_rate_after = calc_q_rate(r2_after['q20_bases'], r2_after['total_bases'])
    r2_q30_rate_after = calc_q_rate(r2_after['q30_bases'], r2_after['total_bases'])

    # Overall statistics
    total_bases_before = r1_before['total_bases'] + r2_before['total_bases']
    total_bases_after = r1_after['total_bases'] + r2_after['total_bases']
    total_q20_before = r1_before['q20_bases'] + r2_before['q20_bases']
    total_q30_before = r1_before['q30_bases'] + r2_before['q30_bases']
    total_q20_after = r1_after['q20_bases'] + r2_after['q20_bases']
    total_q30_after = r1_after['q30_bases'] + r2_after['q30_bases']

    overall_q20_rate_before = calc_q_rate(total_q20_before, total_bases_before)
    overall_q30_rate_before = calc_q_rate(total_q30_before, total_bases_before)
    overall_q20_rate_after = calc_q_rate(total_q20_after, total_bases_after)
    overall_q30_rate_after = calc_q_rate(total_q30_after, total_bases_after)

    # Calculate mean quality scores from quality curves
    def calc_mean_quality(qual_curves):
        mean_qual = qual_curves['mean']
        return round(sum(mean_qual) / len(mean_qual), 2)

    r1_mean_quality = calc_mean_quality(r1_before['quality_curves'])
    r2_mean_quality = calc_mean_quality(r2_before['quality_curves'])

    # Calculate mean GC content from content curves
    def calc_mean_gc(content_curves):
        gc = content_curves['GC']
        return round(sum(gc) / len(gc) * 100, 2)

    r1_mean_gc = calc_mean_gc(r1_before['content_curves'])
    r2_mean_gc = calc_mean_gc(r2_before['content_curves'])

    # Count overrepresented sequences
    r1_overrepresented = len(r1_before.get('overrepresented_sequences', {}))
    r2_overrepresented = len(r2_before.get('overrepresented_sequences', {}))

    # Calculate filtering percentages
    total_reads = before['total_reads']
    passed_reads = filtering['passed_filter_reads']
    filtered_reads = total_reads - passed_reads
    filter_rate = round((filtered_reads / total_reads) * 100, 2) if total_reads > 0 else 0.0

    # Count overrepresented sequences in total data
    total_overrepresented = r1_overrepresented + r2_overrepresented

    stats = {
        # Sample identification
        'sample': sample,

        # Overall summary statistics (before filtering)
        'total_reads_before': before['total_reads'],
        'total_bases_before': before['total_bases'],
        'read1_mean_length_before': before['read1_mean_length'],
        'read2_mean_length_before': before['read2_mean_length'],
        'gc_content_before': round(before['gc_content'] * 100, 2),
        'q20_rate_before': round(before['q20_rate'] * 100, 2),
        'q30_rate_before': round(before['q30_rate'] * 100, 2),

        # Overall summary statistics (after filtering)
        'total_reads_after': after['total_reads'],
        'total_bases_after': after['total_bases'],
        'read1_mean_length_after': after['read1_mean_length'],
        'read2_mean_length_after': after['read2_mean_length'],
        'gc_content_after': round(after['gc_content'] * 100, 2),
        'q20_rate_after': round(after['q20_rate'] * 100, 2),
        'q30_rate_after': round(after['q30_rate'] * 100, 2),

        # R1 specific statistics (before filtering)
        'r1_total_reads_before': r1_before['total_reads'],
        'r1_total_bases_before': r1_before['total_bases'],
        'r1_q20_bases_before': r1_before['q20_bases'],
        'r1_q30_bases_before': r1_before['q30_bases'],
        'r1_q20_rate_before': r1_q20_rate,
        'r1_q30_rate_before': r1_q30_rate,
        'r1_mean_quality_before': r1_mean_quality,
        'r1_mean_gc_before': r1_mean_gc,
        'r1_overrepresented_sequences': r1_overrepresented,
        'r1_total_cycles': r1_before['total_cycles'],

        # R1 specific statistics (after filtering)
        'r1_total_reads_after': r1_after['total_reads'],
        'r1_total_bases_after': r1_after['total_bases'],
        'r1_q20_bases_after': r1_after['q20_bases'],
        'r1_q30_bases_after': r1_after['q30_bases'],
        'r1_q20_rate_after': r1_q20_rate_after,
        'r1_q30_rate_after': r1_q30_rate_after,

        # R2 specific statistics (before filtering)
        'r2_total_reads_before': r2_before['total_reads'],
        'r2_total_bases_before': r2_before['total_bases'],
        'r2_q20_bases_before': r2_before['q20_bases'],
        'r2_q30_bases_before': r2_before['q30_bases'],
        'r2_q20_rate_before': r2_q20_rate,
        'r2_q30_rate_before': r2_q30_rate,
        'r2_mean_quality_before': r2_mean_quality,
        'r2_mean_gc_before': r2_mean_gc,
        'r2_overrepresented_sequences': r2_overrepresented,
        'r2_total_cycles': r2_before['total_cycles'],

        # R2 specific statistics (after filtering)
        'r2_total_reads_after': r2_after['total_reads'],
        'r2_total_bases_after': r2_after['total_bases'],
        'r2_q20_bases_after': r2_after['q20_bases'],
        'r2_q30_bases_after': r2_after['q30_bases'],
        'r2_q20_rate_after': r2_q20_rate_after,
        'r2_q30_rate_after': r2_q30_rate_after,

        # Overall combined statistics (calculated from R1+R2)
        'overall_q20_rate_before': overall_q20_rate_before,
        'overall_q30_rate_before': overall_q30_rate_before,
        'overall_q20_rate_after': overall_q20_rate_after,
        'overall_q30_rate_after': overall_q30_rate_after,

        # Filtering statistics
        'passed_filter_reads': filtering['passed_filter_reads'],
        'low_quality_reads': filtering['low_quality_reads'],
        'too_many_n_reads': filtering['too_many_N_reads'],
        'too_short_reads': filtering['too_short_reads'],
        'too_long_reads': filtering['too_long_reads'],
        'filtered_reads': filtered_reads,
        'filter_rate_percent': filter_rate,
        'total_overrepresented_sequences': total_overrepresented,

        # Duplication metrics
        'duplication_rate': round(duplication['rate'] * 100, 2),

        # Insert size metrics
        'insert_size_peak': insert_size['peak'],
        'insert_size_unknown': insert_size['unknown'],
    }

    return stats


def main():
    # Get input and output files from Snakemake or command line
    if len(sys.argv) == 3:
        json_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Fallback: use Snakemake workflow object if available
        try:
            json_file = snakemake.input[0]
            output_file = snakemake.output[0]
        except NameError:
            print("Usage: python extract_fastp_stats.py <input.json> <output.tsv>")
            sys.exit(1)

    # Extract statistics
    stats = extract_fastp_stats(json_file)

    # Create DataFrame and save as TSV
    df = pd.DataFrame([stats])
    df.to_csv(output_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
