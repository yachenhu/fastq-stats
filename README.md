# FASTQ Stats Pipeline

A Snakemake-based pipeline for organizing and verifying FASTQ sequencing data through symlinking and MD5 checksum generation.

## Overview

This pipeline processes raw FASTQ files by:
1. Creating symlinks from source FASTQ files to a standardized directory structure
2. Generating MD5 checksums for data integrity verification

The pipeline uses a modular Snakemake workflow with separate rule files for different processing stages.

## Project Structure

```
fastq-stats/
├── config/
│   ├── config.yaml       # Main configuration file
│   ├── samples.tsv       # Sample metadata table
│   └── units.tsv         # Sample units with FASTQ paths
├── workflow/
│   ├── Snakefile         # Main workflow entry point
│   ├── rules/
│   │   ├── common.smk    # Common utilities and data loading
│   │   ├── input.smk     # Input file handling rules
│   │   └── qc.smk        # Quality control rules (placeholder)
│   └── envs/
│       └── hashdeep.yaml # Conda environment for MD5 generation
└── results/
    └── fastq/
        └── raw/          # Output directory for symlinks and MD5 files
```

## Configuration

### Main Configuration (`config/config.yaml`)

```yaml
samples: config/samples.tsv
units: config/units.tsv

processing:
  trimming:
    tool: fastp
    skip: false

params:
  fastp:
    adapters: null
    extra: "--disable_adapter_trimming --disable_quality_filtering"
```

### Sample Configuration Files

- **`samples.tsv`**: Sample metadata with sample names as index
- **`units.tsv`**: Sample units with columns for `r1` and `r2` specifying paths to FASTQ files

Example `units.tsv` format:
```
sample  r1                              r2
SAMP1   /path/to/SAMP1_R1.fastq.gz     /path/to/SAMP1_R2.fastq.gz
SAMP2   /path/to/SAMP2_R1.fastq.gz     /path/to/SAMP2_R2.fastq.gz
```

## Usage

### Prerequisites

- Python 3.6+
- Snakemake 7.0+
- Conda (for environment management)

### Running the Pipeline

```bash
# Run with default settings
snakemake --use-conda

# Run with specific number of threads
snakemake --use-conda --cores 8

# Dry run to see what will be executed
snakemake --use-conda --dry-run
```

### Clean Up

```bash
# Remove all generated files
snakemake clean
```

## Rules

### Common Rules (`rules/common.smk`)

- Loads sample and unit tables from TSV files
- Provides `get_fastqs()` function to retrieve FASTQ paths for a sample

### Input Rules (`rules/input.smk`)

1. **`link_fastq`**: Creates symlinks from source FASTQ files to standardized output paths
   - Input: R1 and R2 FASTQ files specified in units.tsv
   - Output: Symlinks in `results/fastq/raw/{sample}_R1.fastq.gz` and `{sample}_R2.fastq.gz`

2. **`md5_fastq`**: Generates MD5 checksums for FASTQ files
   - Input: FASTQ file
   - Output: `.md5` file containing MD5 hash
   - Uses: hashdeep (8 threads)

### QC Rules (`rules/qc.smk`)

Contains commented-out rules for future fastp quality control implementation.

## Output

The pipeline generates:

```
results/fastq/raw/
├── {sample}_R1.fastq.gz          # Symlink to R1 FASTQ
├── {sample}_R1.fastq.gz.md5      # MD5 checksum for R1
├── {sample}_R2.fastq.gz          # Symlink to R2 FASTQ
└── {sample}_R2.fastq.gz.md5      # MD5 checksum for R2
```

## Environment

The pipeline uses Conda environments for reproducibility:

- **`hashdeep.yaml`**: Provides hashdeep 4.4 for MD5 checksum generation

## Future Development

The pipeline includes placeholder code for:
- FASTP-based quality control and trimming
- QC summary generation and merging
- Adapter trimming and quality filtering

These features are currently commented out and can be enabled when needed.

## Notes

- The pipeline creates symlinks rather than copying files to save disk space
- MD5 checksums provide data integrity verification for downstream analysis
- All paths in configuration files should be absolute or relative to the working directory
