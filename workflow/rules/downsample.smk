"""
Downsample Module

This module uses seqtk to downsample FASTQ files to a target size.
"""

rule downsample_fastq:
    """
    Downsample FASTQ files to target size (1-2 GB) using seqtk.

    Seqtk sample downsamples reads by a specified fraction. The fraction
    is calculated to achieve the target file size based on input size.
    """
    input:
        f1 = "results/{sample}/reads/{sample}_R1.fastq.gz",
        f2 = "results/{sample}/reads/{sample}_R2.fastq.gz"
    output:
        f1 = "results/{sample}/downsample/{sample}_R1.fastq.gz",
        f2 = "results/{sample}/downsample/{sample}_R2.fastq.gz"
    params:
        command="sample",
        # Target size in GB (configurable, default 1-2 GB range)
        n = lambda wildcards: str_to_random(wildcards.sample, 1.25, 2.0) * 1e9 / 150,
        # Seed for reproducible sampling
        extra = config["params"]["seqtk"]["sample"]
    threads:
        8
    wrapper:
        "v4.3.0/bio/seqtk"


rule md5_downsample:
    """
    Create .md5 files for downsampled FASTQ files.
    """
    input:
        "results/{sample}/downsample/{sample}_{read}.fastq.gz"
    output:
        "results/{sample}/downsample/{sample}_{read}.fastq.gz.md5"
    threads:
        8
    conda:
        "../envs/hashdeep.yaml"
    shell:
        "hashdeep -j {threads} -c md5 -b {input} | "
        "tail -1 | cut -d',' -f2-3 | sed 's/,/\  /' "
        ">{output}"
