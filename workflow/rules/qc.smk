"""
FASTP Quality Control Module

This module uses fastp to calculate Q20 and Q30 statistics for raw FASTQ files.
Fastp provides comprehensive quality metrics including base quality distributions.
"""

rule fastp_qc:
    """
    Run fastp quality control on raw FASTQ files to calculate Q20 and Q30 statistics.

    Fastp generates JSON output containing detailed quality metrics including:
    - Q20 percentage (bases with quality score >= 20)
    - Q30 percentage (bases with quality score >= 30)
    - Overall quality statistics for both R1 and R2 reads
    """
    input:
        sample=[
            "results/{sample}/reads/{sample}_R1.fastq.gz",
            "results/{sample}/reads/{sample}_R2.fastq.gz"
        ]
    output:
        json = "results/{sample}/fastp/{sample}.json",
        html = "results/{sample}/fastp/{sample}.html"
    params:
        # Disable adapter trimming and quality filtering to get raw statistics
        extra = config["params"]["fastp"]["extra"]
    threads:
        8
    log:
        "logs/fastp_qc/{sample}.log"
    benchmark:
        "benchmarks/fastp_qc/{sample}.txt"
    wrapper:
        "v4.3.0/bio/fastp"


rule extract_fastp_stats:
    """
    Extract statistics from fastp JSON output.

    This rule parses the fastp JSON output and creates a summary table.
    """
    input:
        "results/{sample}/fastp/{sample}.json"
    output:
        temp("results/{sample}/fastp/{sample}.tsv")
    conda:
        "../envs/python.yaml"
    script:
        "../scripts/extract_fastp_stats.py"


rule merge_fastp_stats:
    """
    Merge fastp statistics from all samples.
    """
    input:
        expand("results/{sample}/fastp/{sample}.tsv", sample=unit_table.index)
    output:
        "results/merged/fastp_stats.tsv"
    conda:
        "../envs/csvtk.yaml"
    shell:
        "csvtk -t concat {input} -o {output}"


rule fetch_total_bases_q20_q30:
    """
    Fetch total gigabases, Q20 bases, and Q30 bases from fastp statistics.
    """
    input:
        "results/merged/fastp_stats.tsv"
    output:
        "results/merged/fastp_stats_q20_q30.tsv"
    conda:
        "../envs/csvtk.yaml"
    shell:
        "cat {input} | "
        "csvtk -t mutate2 -n 'Total_bases' -e ' $total_bases_before / 1000000000' | "
        "csvtk -t rename -f q20_rate_before -n 'Q20' | "
        "csvtk -t rename -f q30_rate_before -n 'Q30' | "
        "csvtk -t cut -f'sample,Total_bases,Q20,Q30' "
        "-o {output}"
