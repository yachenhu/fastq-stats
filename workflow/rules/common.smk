import pandas as pd
import random

sample_table = pd.read_table(config["samples"], index_col=0)
unit_table = pd.read_table(config["units"], index_col=0)

def get_fastqs(wildcards):
    """
    Get fastq files for a sample.
    """
    return [unit_table.loc[wildcards.sample, "r1"],
            unit_table.loc[wildcards.sample, "r2"]]


def str_to_random(s, min_val, max_val):
    """
    将字符串转换为 min_val 到 max_val 之间的随机数
    """
    # 用字符串的哈希值作为随机种子，保证相同字符串得到相同结果
    random.seed(hash(s))
    return random.uniform(min_val, max_val)
