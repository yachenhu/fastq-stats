import pandas as pd

sample_table = pd.read_table(config["samples"], index_col=0)
unit_table = pd.read_table(config["units"], index_col=0)

def get_fastqs(wildcards):
    """
    Get fastq files for a sample.
    """
    return [unit_table.loc[wildcards.sample, "r1"],
            unit_table.loc[wildcards.sample, "r2"]]
