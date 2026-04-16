# FASTQ Stats Pipeline

A Snakemake-based pipeline for organizing FASTQ sequencing data and performing comprehensive quality control analysis.

## Overview

This pipeline processes raw FASTQ files by:
1. Creating symlinks from source FASTQ files to a standardized directory structure
2. Generating MD5 checksums for data integrity verification
3. Running comprehensive quality control analysis using fastp
4. Extracting and merging detailed QC metrics from fastp output

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
│   │   └── qc.smk        # Quality control rules
│   ├── scripts/
│   │   ├── extract_fastp_stats.py   # Extract comprehensive fastp statistics
│   │   └── merge_q20_q30.py       # Merge fastp statistics from multiple samples
│   └── envs/
│       ├── hashdeep.yaml   # Conda environment for MD5 generation
│       ├── python.yaml     # Conda environment for Python scripts
│       └── csvtk.yaml     # Conda environment for CSV manipulation
└── results/
    ├── {sample}/           # Per-sample directory
    │   ├── reads/          # MD5 checksums
    │   └── fastp/         # fastp QC output (JSON, HTML)
    └── merged/            # Merged statistics across all samples
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
SAMP1   /path/to/SAMP1_R1.fastq.gz     /path/to/SAMP2_R2.fastq.gz
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

# Clean all generated files
snakemake clean
```

## Rules

### Common Rules (`rules/common.smk`)

- Loads sample and unit tables from TSV files
- Provides `get_fastqs()` function to retrieve FASTQ paths for a sample

### Input Rules (`rules/input.smk`)

1. **`link_fastq`**: Creates symlinks from source FASTQ files to standardized output paths
   - Input: R1 and R2 FASTQ files specified in units.tsv
   - Output: Symlinks in `results/{sample}/reads/{sample}_R1.fastq.gz` and `{sample}_R2.fastq.gz`

2. **`md5_fastq`**: Generates MD5 checksums for FASTQ files
   - Input: FASTQ file
   - Output: `.md5` file containing MD5 hash
   - Uses: hashdeep (8 threads)

### QC Rules (`rules/qc.smk`)

1. **`fastp_qc`**: Runs fastp quality control on raw FASTQ files
   - Input: R1 and R2 FASTQ files
   - Output: JSON and HTML reports in `results/{sample}/fastp/`
   - Generates: Comprehensive quality metrics including Q20/Q30 rates, filtering stats, duplication, insert size

2. **`extract_fastp_stats`**: Extracts comprehensive statistics from fastp JSON output
   - Input: fastp JSON file
   - Output: TSV file with 50+ quality metrics
   - Metrics include: basic stats, quality metrics, filtering statistics, duplication, insert size, per-read breakdown

3. **`merge_fastp_stats`**: Merges fastp statistics from all samples
   - Input: Individual sample stats files
   - Output: Consolidated table `results/merged/fastp_stats.tsv`

4. **`fetch_total_bases_q20_q30`**: Extracts key metrics from merged statistics
   - Input: Merged fastp stats
   - Output: Simplified table with total bases, Q20, and Q30 metrics

## Output

The pipeline generates a per-sample directory structure:

```
results/{sample}/
├── reads/
│   ├── {sample}_R1.fastq.gz.md5      # MD5 checksum for R1
│   └── {sample}_R2.fastq.gz.md5      # MD5 checksum for R2
└── fastp/
    ├── {sample}.json                   # fastp JSON output
    └── {sample}.html                   # fastp HTML report
```

And merged results:

```
results/merged/
├── fastp_stats.tsv                     # Comprehensive fastp statistics (50+ metrics)
└── fastp_stats_q20_q30.tsv            # Simplified key metrics
```

### Comprehensive Fastp Statistics

The `fastp_stats.tsv` file contains over 50 metrics including:

#### Overall Statistics
- Total reads and bases (before/after filtering)
- Read length for R1 and R2
- GC content
- Q20 and Q30 rates

#### Per-Read Statistics (R1 and R2 separately)
- Total reads and bases
- Q20 and Q30 base counts and rates
- Mean quality scores
- Mean GC content
- Overrepresented sequences count

#### Filtering Statistics
- Passed filter reads
- Low quality reads
- Too many N reads
- Too short/long reads
- Overall filter rate percentage

#### Additional Metrics
- Duplication rate
- Insert size distribution (peak, unknown)
- Overall combined Q20/Q30 rates

## Environment

The pipeline uses Conda environments for reproducibility:

- **`hashdeep.yaml`**: Provides hashdeep 4.4 for MD5 checksum generation
- **`python.yaml`**: Provides Python and pandas for statistics extraction
- **`csvtk.yaml`**: Provides csvtk for CSV/TSV manipulation

## Scripts

### `extract_fastp_stats.py`

Extracts comprehensive statistics from fastp JSON output. Generates a TSV file with over 50 quality metrics including basic stats, quality metrics, filtering statistics, duplication rates, insert size metrics, and per-read breakdown.

### `merge_q20_q30.py`

Merges fastp statistics from multiple samples into a single consolidated table for downstream analysis and reporting.

## Notes

- The pipeline creates symlinks rather than copying files to save disk space
- MD5 checksums provide data integrity verification for downstream analysis
- fastp is configured without adapter trimming or quality filtering to obtain raw statistics
- All paths in configuration files should be absolute or relative to working directory
- The pipeline assumes paired-end sequencing data with R1/R2 files
