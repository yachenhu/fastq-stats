rule link_fastq:
    """
    Symlink and rename raw fastq files into working directory.
    """
    input:
        r1 = lambda wildcards: unit_table.loc[wildcards.sample, "r1"],
        r2 = lambda wildcards: unit_table.loc[wildcards.sample, "r2"]
    output:
        r1 = "results/{sample}/reads/{sample}_R1.fastq.gz",
        r2 = "results/{sample}/reads/{sample}_R2.fastq.gz"
    shell:
        "DIR=$(dirname {output.r1}); " 
        "mkdir -p $DIR && "
        "ln -sf {input.r1:q} {output.r1} && "
        "ln -sf {input.r2:q} {output.r2}"

rule md5_fastq:
    """
    Create .md5 files for fastq files.
    """
    input:
        "results/{sample}/reads/{sample}_{read}.fastq.gz",
    output:
        "results/{sample}/reads/{sample}_{read}.fastq.gz.md5", 
    threads:
        8
    conda:
        "../envs/hashdeep.yaml"
    shell:
        "hashdeep -j {threads} -c md5 -b {input} | "
        "tail -1 | cut -d',' -f2-3 | sed 's/,/\  /' "
        ">{output}"
