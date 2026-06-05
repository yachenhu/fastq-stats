# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Pipeline Overview

A Snakemake pipeline for paired-end FASTQ QC: symlinks source files, conditionally downsamples with seqtk (if total size > 1 GB, ~6M read pairs with per-sample randomization), and runs fastp to produce a comprehensive QC table (62 columns).

## Running the Pipeline

```bash
snakemake --use-conda --conda-prefix ~/.snakemake/conda --wrapper-prefix https://gitee.com/yachenhu/snakemake-wrappers/raw/ --cores 8
snakemake --use-conda --dry-run          # show DAG
```

## Architecture

All rules are defined in a single `workflow/Snakefile`.

- **`workflow/Snakefile`** — loads the samples table from config, defines all rules
- **`workflow/scripts/extract_fastp_stats.py`** — extracts 62 comprehensive QC metrics per sample from fastp JSON
- **`workflow/scripts/merge_fastp_stats.py`** — merges per-sample TSVs into the final QC table
- **`workflow/envs/hashdeep.yaml`** — hashdeep 4.4 for MD5 checksums
- **`workflow/envs/seqtk.yaml`** — seqtk 1.4 for downsampling
- **`workflow/envs/python.yaml`** — Python 3.10 with pandas

### Rules

1. `prepare_fastq` — symlinks source FASTQs to `processed_data/{sample}/`; if total size > 1 GB, downsamples with seqtk (n≈5.9M–6.1M per sample, derived from stable hash of sample name, seed=100)
2. `md5_fastq` — MD5 checksums for the prepared FASTQs (hashdeep, 8 threads)
3. `fastp_qc` — fastp with adapter trimming and quality filtering disabled (v4.3.0 wrapper)
4. `extract_fastp_stats` — extracts 62 QC metrics per sample from fastp JSON
5. `merge_fastp_stats` — merges per-sample TSVs into `results/merged/qc.tsv`

### Configuration

**`config/config.yaml`**:
```yaml
samples: config/samples.tsv
fastp:
  extra: "--disable_adapter_trimming --disable_quality_filtering"
```

**`config/samples.tsv`**: Tab-separated file with columns `sample_name`, `library_name`, `r1`, `r2`. Indexed by `sample_name`.

### Output Structure

```
processed_data/{sample}/{sample}_{R1,R2}.fastq.gz      # symlinks or downsampled FASTQs
processed_data/{sample}/{sample}_{R1,R2}.fastq.gz.md5  # MD5 checksums
results/{sample}/fastp/{sample}.json                    # fastp QC output
results/{sample}/fastp/{sample}.html
results/merged/qc.tsv                                   # final QC summary (62 columns)
```
