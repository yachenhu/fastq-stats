# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Pipeline Overview

This is a minimal Snakemake pipeline for organizing and verifying FASTQ sequencing data. The pipeline creates symlinks from source FASTQ files to a standardized directory structure and generates MD5 checksums for data integrity verification.

## Running the Pipeline

```bash
# Run with conda environments and default core count
snakemake --use-conda

# Run with specific number of cores
snakemake --use-conda --cores 8

# Dry run to see what will be executed
snakemake --use-conda --dry-run

# Clean all generated files
snakemake clean
```

## Architecture

### Modular Workflow Structure

The workflow uses Snakemake's `include` directive to modularize rules:

- **`workflow/Snakefile`**: Entry point that loads config and includes rule files
- **`workflow/rules/common.smk`**: Defines shared utilities and loads pandas DataFrames
- **`workflow/rules/input.smk`**: Handles input file processing (symlinking, MD5 generation)
- **`workflow/rules/qc.smk`**: Placeholder for future quality control rules (currently commented out)

### Data Loading Pattern

The pipeline uses pandas to load TSV configuration files into DataFrames that are accessed by rules:

```python
sample_table = pd.read_table(config["samples"], index_col=0)
unit_table = pd.read_table(config["units"], index_col=0)
```

The `unit_table` is indexed by sample name and contains `r1` and `r2` columns with FASTQ file paths.

### Key Functions

- **`get_fastqs(wildcards)`**: Returns `[r1_path, r2_path]` for a given sample from the unit_table

### Configuration Format

**`config/samples.tsv`**: Simple list of sample names with `sample_name` header.

**`config/units.tsv`**: Tab-separated file with columns:
- `sample_name`: Sample identifier (used as index)
- `library_name`: Library identifier
- `r1`: Path to R1 FASTQ file
- `r2`: Path to R2 FASTQ file

All paths should be absolute or relative to the working directory.

### Output Structure

The pipeline generates symlinks and MD5 files in `results/fastq/raw/`:
- `{sample}_R1.fastq.gz` → symlink to R1 FASTQ
- `{sample}_R1.fastq.gz.md5` → MD5 checksum
- `{sample}_R2.fastq.gz` → symlink to R2 FASTQ
- `{sample}_R2.fastq.gz.md5` → MD5 checksum

### Conda Environments

- **`workflow/envs/hashdeep.yaml`**: Provides hashdeep 4.4 for MD5 checksum generation (uses 8 threads)

### Current Implementation

The pipeline currently implements:
1. `link_fastq`: Creates symlinks from source FASTQ files to standardized output paths
2. `md5_fastq`: Generates MD5 checksums using hashdeep with parallel processing

### Future Development

The `qc.smk` file contains commented-out rules for fastp-based quality control and trimming. These are not currently functional and would require:
- Implementing `get_fastp_adapters()` and `get_fastp_params()` helper functions
- Creating scripts directory with `parse_fastp_json.py`
- Adding additional conda environments (e.g., `csvtk.yaml`)

### Important Notes

- The pipeline uses symlinks rather than copying files to save disk space
- The `rule all` in `Snakefile` defines the final targets (MD5 files for all samples and reads)
- Configuration is centralized in `config/config.yaml` with paths to TSV files
- The workflow assumes paired-end sequencing data with R1/R2 files