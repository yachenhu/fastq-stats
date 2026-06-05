# FASTQ Stats Pipeline

A Snakemake pipeline for paired-end FASTQ QC: symlinks source files, conditionally downsamples with seqtk, and runs fastp to produce a comprehensive 62-column QC table.

## Overview

1. Symlinks or downsamples source FASTQs into `processed_data/`
2. Generates MD5 checksums for data integrity
3. Runs fastp QC (no adapter trimming, no quality filtering)
4. Extracts 62 comprehensive QC metrics per sample
5. Merges into a single `qc.tsv` table

## Project Structure

```
fastq-stats/
├── config/
│   ├── config.yaml          # Pipeline configuration
│   └── samples.tsv          # Sample table (sample, library, r1, r2)
├── workflow/
│   ├── Snakefile            # All rules in one file
│   ├── scripts/
│   │   ├── extract_fastp_stats.py   # 62-column per-sample extraction
│   │   └── merge_fastp_stats.py    # Merge into final qc.tsv
│   └── envs/
│       ├── hashdeep.yaml    # MD5 checksums
│       ├── seqtk.yaml       # Downsampling
│       └── python.yaml      # Python + pandas
├── processed_data/          # FASTQ layer (generated)
└── results/                 # Analysis layer (generated)
```

## Configuration

### `config/config.yaml`

```yaml
samples: config/samples.tsv
fastp:
  extra: "--disable_adapter_trimming --disable_quality_filtering"
```

### `config/samples.tsv`

Tab-separated, indexed by `sample_name`:

```
sample_name  library_name  r1                            r2
library-1    lib1          /path/to/sample_R1.fastq.gz   /path/to/sample_R2.fastq.gz
6-L-9-SP     6L-9-SP       /path/to/sample_R1.fastq.gz   /path/to/sample_R2.fastq.gz
```

## Usage

```bash
# Full run
snakemake --use-conda --conda-prefix ~/.snakemake/conda \
  --wrapper-prefix https://gitee.com/yachenhu/snakemake-wrappers/raw/ \
  --cores 8

# Dry run
snakemake --use-conda --dry-run
```

## Rules

1. **`prepare_fastq`** — Symlinks source FASTQs; if total size > 1 GB, downsamples with seqtk (~5.9M–6.1M read pairs per sample, deterministic via stable hash of sample name, seed=100)
2. **`md5_fastq`** — MD5 checksums (hashdeep, 8 threads)
3. **`fastp_qc`** — fastp QC (v4.3.0 wrapper, 8 threads)
4. **`extract_fastp_stats`** — Extracts 62 QC metrics per sample from fastp JSON
5. **`merge_fastp_stats`** — Merges all samples into final QC table

## Output Structure

```
processed_data/{sample}/{sample}_{R1,R2}.fastq.gz       # FASTQ + MD5
results/{sample}/fastp/{sample}.json, .html             # Per-sample fastp
results/merged/qc.tsv                                   # Final QC table (62 columns)
```

## QC Metrics (62 columns)

| Category | Metrics |
|----------|---------|
| Overall (before/after) | total_reads, total_bases, mean_length, gc_content, q20/q30_rate |
| R1 (before/after) | reads, bases, q20/q30 bases & rates, mean quality, mean GC, overrepresented sequences, cycles |
| R2 (before/after) | reads, bases, q20/q30 bases & rates, mean quality, mean GC, overrepresented sequences, cycles |
| Combined | overall_q20/q30_rate (before/after) |
| Filtering | passed, low_quality, too_many_n, too_short, too_long, filtered_reads, filter_rate |
| Other | duplication_rate, insert_size_peak, insert_size_unknown |
