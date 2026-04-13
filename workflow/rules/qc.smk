rule symlink:
    input:
        get_fastqs
    output:
        []
    shell:


# rule fastp_pe:
#     input:
#         sample=get_fastqs
#     output:
#         json = "results/{sample}/qc/fastp/{sample}.json",
#         html = "results/{sample}/qc/fastp/{sample}.html"
#     params:
#         adapters = get_fastp_adapters,
#         extra = get_fastp_params
#     threads:
#         8
#     log:
#         "logs/fastp_pe/{sample}-{unit}.log"
#     benchmark:
#         "benchmarks/fastp_pe/{sample}-{unit}.txt"
#     wrapper:
#         "v4.3.0/bio/fastp"


# rule fastp_summary:
#     input:
#         get_fastp_json
#     output:
#         "results/{sample}/qc/fastp/{sample}.summary.tsv"
#     script:
#         "../scripts/parse_fastp_json.py"


# rule fastp_summary_merge:
#     input:
#         expand("results/{sample}/qc/fastp/{sample}.summary.tsv", sample=samples)
#     output:
#         summary = "results/merged/qc/fastp.summary.tsv"
#     conda:
#         "../envs/csvtk.yaml"
#     shell:
#         "csvtk -t concat {input} > {output}"
