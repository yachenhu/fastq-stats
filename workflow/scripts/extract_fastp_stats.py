#!/usr/bin/env python3
"""
Extract comprehensive statistics from fastp JSON output.

Parses fastp JSON and extracts quality, filtering, duplication, insert size,
and per-read (R1/R2) metrics — over 50 columns per sample.
"""

import json
import sys
import pandas as pd
from pathlib import Path


def calc_q_rate(q_bases, total_bases):
    return round((q_bases / total_bases) * 100, 2) if total_bases > 0 else 0.0


def calc_mean_from_curve(curve):
    if not curve:
        return 0.0
    return round(sum(curve) / len(curve), 2)


def extract_fastp_stats(json_file):
    with open(json_file) as f:
        data = json.load(f)

    sample = Path(json_file).stem
    summary = data["summary"]
    before = summary["before_filtering"]
    after = summary["after_filtering"]
    filtering = data["filtering_result"]
    duplication = data["duplication"]
    insert_size = data["insert_size"]

    r1_before = data["read1_before_filtering"]
    r2_before = data["read2_before_filtering"]
    r1_after = data["read1_after_filtering"]
    r2_after = data["read2_after_filtering"]

    r1_q20_rate = calc_q_rate(r1_before["q20_bases"], r1_before["total_bases"])
    r1_q30_rate = calc_q_rate(r1_before["q30_bases"], r1_before["total_bases"])
    r1_q20_rate_after = calc_q_rate(r1_after["q20_bases"], r1_after["total_bases"])
    r1_q30_rate_after = calc_q_rate(r1_after["q30_bases"], r1_after["total_bases"])

    r2_q20_rate = calc_q_rate(r2_before["q20_bases"], r2_before["total_bases"])
    r2_q30_rate = calc_q_rate(r2_before["q30_bases"], r2_before["total_bases"])
    r2_q20_rate_after = calc_q_rate(r2_after["q20_bases"], r2_after["total_bases"])
    r2_q30_rate_after = calc_q_rate(r2_after["q30_bases"], r2_after["total_bases"])

    total_bases_before = r1_before["total_bases"] + r2_before["total_bases"]
    total_bases_after = r1_after["total_bases"] + r2_after["total_bases"]
    total_q20_before = r1_before["q20_bases"] + r2_before["q20_bases"]
    total_q30_before = r1_before["q30_bases"] + r2_before["q30_bases"]
    total_q20_after = r1_after["q20_bases"] + r2_after["q20_bases"]
    total_q30_after = r1_after["q30_bases"] + r2_after["q30_bases"]

    overall_q20_rate_before = calc_q_rate(total_q20_before, total_bases_before)
    overall_q30_rate_before = calc_q_rate(total_q30_before, total_bases_before)
    overall_q20_rate_after = calc_q_rate(total_q20_after, total_bases_after)
    overall_q30_rate_after = calc_q_rate(total_q30_after, total_bases_after)

    r1_mean_quality = calc_mean_from_curve(r1_before.get("quality_curves", {}).get("mean", []))
    r2_mean_quality = calc_mean_from_curve(r2_before.get("quality_curves", {}).get("mean", []))
    r1_mean_gc = calc_mean_from_curve(r1_before.get("content_curves", {}).get("GC", []))
    r2_mean_gc = calc_mean_from_curve(r2_before.get("content_curves", {}).get("GC", []))

    r1_overrepresented = len(r1_before.get("overrepresented_sequences", {}))
    r2_overrepresented = len(r2_before.get("overrepresented_sequences", {}))

    total_reads = before["total_reads"]
    passed_reads = filtering["passed_filter_reads"]
    filtered_reads = total_reads - passed_reads
    filter_rate = round((filtered_reads / total_reads) * 100, 2) if total_reads > 0 else 0.0

    return {
        "sample": sample,

        # Before filtering — overall
        "total_reads_before": before["total_reads"],
        "total_bases_before": before["total_bases"],
        "read1_mean_length_before": before["read1_mean_length"],
        "read2_mean_length_before": before["read2_mean_length"],
        "gc_content_before": round(before["gc_content"] * 100, 2),
        "q20_rate_before": round(before["q20_rate"] * 100, 2),
        "q30_rate_before": round(before["q30_rate"] * 100, 2),

        # After filtering — overall
        "total_reads_after": after["total_reads"],
        "total_bases_after": after["total_bases"],
        "read1_mean_length_after": after["read1_mean_length"],
        "read2_mean_length_after": after["read2_mean_length"],
        "gc_content_after": round(after["gc_content"] * 100, 2),
        "q20_rate_after": round(after["q20_rate"] * 100, 2),
        "q30_rate_after": round(after["q30_rate"] * 100, 2),

        # R1 before
        "r1_total_reads_before": r1_before["total_reads"],
        "r1_total_bases_before": r1_before["total_bases"],
        "r1_q20_bases_before": r1_before["q20_bases"],
        "r1_q30_bases_before": r1_before["q30_bases"],
        "r1_q20_rate_before": r1_q20_rate,
        "r1_q30_rate_before": r1_q30_rate,
        "r1_mean_quality_before": r1_mean_quality,
        "r1_mean_gc_before": r1_mean_gc,
        "r1_overrepresented_sequences": r1_overrepresented,
        "r1_total_cycles": r1_before["total_cycles"],

        # R1 after
        "r1_total_reads_after": r1_after["total_reads"],
        "r1_total_bases_after": r1_after["total_bases"],
        "r1_q20_bases_after": r1_after["q20_bases"],
        "r1_q30_bases_after": r1_after["q30_bases"],
        "r1_q20_rate_after": r1_q20_rate_after,
        "r1_q30_rate_after": r1_q30_rate_after,

        # R2 before
        "r2_total_reads_before": r2_before["total_reads"],
        "r2_total_bases_before": r2_before["total_bases"],
        "r2_q20_bases_before": r2_before["q20_bases"],
        "r2_q30_bases_before": r2_before["q30_bases"],
        "r2_q20_rate_before": r2_q20_rate,
        "r2_q30_rate_before": r2_q30_rate,
        "r2_mean_quality_before": r2_mean_quality,
        "r2_mean_gc_before": r2_mean_gc,
        "r2_overrepresented_sequences": r2_overrepresented,
        "r2_total_cycles": r2_before["total_cycles"],

        # R2 after
        "r2_total_reads_after": r2_after["total_reads"],
        "r2_total_bases_after": r2_after["total_bases"],
        "r2_q20_bases_after": r2_after["q20_bases"],
        "r2_q30_bases_after": r2_after["q30_bases"],
        "r2_q20_rate_after": r2_q20_rate_after,
        "r2_q30_rate_after": r2_q30_rate_after,

        # Overall combined (R1+R2)
        "overall_q20_rate_before": overall_q20_rate_before,
        "overall_q30_rate_before": overall_q30_rate_before,
        "overall_q20_rate_after": overall_q20_rate_after,
        "overall_q30_rate_after": overall_q30_rate_after,

        # Filtering
        "passed_filter_reads": filtering["passed_filter_reads"],
        "low_quality_reads": filtering["low_quality_reads"],
        "too_many_n_reads": filtering["too_many_N_reads"],
        "too_short_reads": filtering["too_short_reads"],
        "too_long_reads": filtering["too_long_reads"],
        "filtered_reads": filtered_reads,
        "filter_rate_percent": filter_rate,
        "total_overrepresented_sequences": r1_overrepresented + r2_overrepresented,

        # Duplication & insert size
        "duplication_rate": round(duplication["rate"] * 100, 2),
        "insert_size_peak": insert_size["peak"],
        "insert_size_unknown": insert_size["unknown"],
    }


def main():
    try:
        json_file = snakemake.input[0]
        output_file = snakemake.output[0]
    except NameError:
        if len(sys.argv) == 3:
            json_file = sys.argv[1]
            output_file = sys.argv[2]
        else:
            print("Usage: python extract_fastp_stats.py <input.json> <output.tsv>")
            sys.exit(1)

    stats = extract_fastp_stats(json_file)
    pd.DataFrame([stats]).to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    main()
