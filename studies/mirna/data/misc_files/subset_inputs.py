#!/usr/bin/env python


__author__ = 'Henry Taylor'
__date__ = '2020-07-27'
__version__ = '0.0.1'

import os
import argparse
from distutils.version import LooseVersion
import pandas as pd
import numpy as np


def subset_vcf(bcf_tool, vsf_file, sample_list, output_dir):
    """Change list of int to comma format."""
    cmd = '{} view -Oz'.format(bcf_tool)
    cmd = '{} -s {}'.format(cmd, ','.join(sample_list))
    cmd = '{} {}'.format(cmd, vsf_file)
    cmd = '{} -o {}/genotypes.vcf.gz'.format(cmd, output_dir)
    os.system(cmd)
    return()


def subset_covariates(cov_file, sample_list):
    covs = pd.read_csv(
        cov_file,
        sep=" ",
        header=0
    )
    smp = [covs.columns[0]]
    smp.extend(sample_list)
    covs = covs[smp]
    return(covs)


def subset_phenotypes(
    pheno_file,
    sample_list,
    min_avg_expr,
    min_expr_cell,
    pct_cells
):
    phenos = pd.read_csv(
        pheno_file,
        sep="\t",
        header=0
    )
    cols = phenos.columns[0:6].tolist()
    cols.extend(sample_list)
    phenos = phenos[cols]

    # Also remove any rows that have an average less than min_avg_expr
    phenos = phenos.loc[(phenos[phenos.columns[6:]].mean(1) >= min_avg_expr), ]

    # Also remove any rows that express a min of `min_expr_cell` in atleast
    # `pct_cells` of cells
    genes_pass_filter = (phenos[phenos.columns[6:]] >= min_expr_cell).sum(1)
    n_smpls = np.ceil(len(phenos[phenos.columns[6:]].columns) * pct_cells)
    phenos = phenos.loc[genes_pass_filter >= n_smpls, ]
    return(phenos)


def main():
    """Run CLI."""
    parser = argparse.ArgumentParser(
        description="""
            Compare results from differential expression tests.
            """
    )

    parser.add_argument(
        '-g', '--genotypes',
        action='store',
        dest='genotypes',
        required=True,
        help='Genotype VCF.'
    )

    parser.add_argument(
        '-pheno', '--phenotype_files',
        action='store',
        dest='phenotypes',
        required=True,
        help='Phenotypes file.'
    )

    parser.add_argument(
        '-covs', '--covariate_file',
        action='store',
        dest='covariates',
        required=True,
        help='Covariate file.'
    )

    parser.add_argument(
        '-samps', '--filter_samples',
        action='store',
        dest='samples',
        required=True,
        help='Samples to retain.'
    )

    parser.add_argument(
        '-min_avg_expr', '--minimum_avg_expression',
        action='store',
        dest='min_avg_expr',
        default=1,
        type=int,
        help='Minimum mean expession to retain in phenotype.'
    )

    parser.add_argument(
        '-min_expr_cell', '--minimum_expression_per_cell',
        action='store',
        dest='min_expr_cell',
        default=0,
        type=float,
        help='Minimum expession across a specific % of cells in phenotype.'
    )

    parser.add_argument(
        '-pct_smpls', '--percent_samples',
        action='store',
        dest='pct_smpls',
        default=0.25,
        type=float,
        help='Percent of samples expressing min_expr_cell'
    )

    parser.add_argument(
        '-of', '--output_dir',
        action='store',
        dest='output_dir',
        required=True,
        help='Output dir.'
    )

    parser.add_argument(
        '-bcf', '--bcf_path',
        action='store',
        dest='bcf',
        required=True,
        help='Output dir.'
    )

    options = parser.parse_args()

    retain_smpls = pd.read_csv(
        options.samples,
        sep='\n',
        header=None,
        low_memory=False
    )[0]

    # First subset vcf
    _ = subset_vcf(
        options.bcf,
        options.genotypes,
        retain_smpls,
        options.output_dir
    )

    # Subset Covs
    covs_df = subset_covariates(options.covariates, retain_smpls)
    compression_opts = 'gzip'
    if LooseVersion(pd.__version__) > '1.0.0':
        compression_opts = dict(method='gzip', compresslevel=9)

    covs_df.to_csv(
        '{}/covariates.txt.gz'.format(options.output_dir),
        sep=' ',
        compression=compression_opts,
        index=False,
        header=True
    )

    # Subset pheno
    pheno_df = subset_phenotypes(
        options.phenotypes,
        retain_smpls,
        options.min_avg_expr,
        options.min_expr_cell,
        options.pct_smpls
    )
    pheno_df.to_csv(
        '{}/moltraits.bed'.format(options.output_dir),
        sep='\t',
        index=False,
        header=True
    )
    # Need to bgzip it
    os.system("bgzip {}/moltraits.bed".format(options.output_dir))


if __name__ == '__main__':
    main()
