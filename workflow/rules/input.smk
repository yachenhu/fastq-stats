RESULTS = "results/fastq/raw/"

rule link_fastq:
    """
    Symlink and rename raw fastq files into working directory.
    """
    input:
        r1 = lambda wildcards: unit_table.loc[wildcards.sample, "r1"],
        r2 = lambda wildcards: unit_table.loc[wildcards.sample, "r2"]
    output:
        r1 = f"{RESULTS}" + "{sample}_R1.fastq.gz",
        r2 = f"{RESULTS}" + "{sample}_R2.fastq.gz"
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
        f"{RESULTS}" + "{prefix}.fastq.gz",
    output:
        f"{RESULTS}" + "{prefix}.fastq.gz.md5",
    threads:
        8
    conda:
        "../envs/hashdeep.yaml"
    shell:
        "hashdeep -j {threads} -c md5 -b {input} | "
        "tail -1 | cut -d',' -f2-3 | sed 's/,/\  /' "
        ">{output}"

# rule all_input:
#     """
#     Create symlinks and md5 files for all samples.
#     """
#     input:
#         expand(
#             [
#                 "{}/{sample}_R1.fastq.gz".format(WORKDIR_FASTQ),
#                 "{}/{sample}_R1.fastq.gz.md5".format(WORKDIR_FASTQ),
#                 "{}/{sample}_R2.fastq.gz".format(WORKDIR_FASTQ),
#                 "{}/{sample}_R2.fastq.gz.md5".format(WORKDIR_FASTQ)
#             ],
#             sample=unit_table.index
#         )
