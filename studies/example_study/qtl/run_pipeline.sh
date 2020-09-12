#!/bin/sh

## Activate QTL conda environment
source activate qtl

## Set any necessary env variables
export SNK_DIR="/cluster/ifs/projects/collins/taylorhj/projects/snakemake-qtl"

## need to add to path to work in pipeline
export PATH="${SNK_DIR}/lib/bin/qtl_tools:$PATH"
export PATH="${SNK_DIR}/lib/bin/veqtl_mapper:$PATH"

snakemake \
     --snakefile ${SNK_DIR}/pipelines/qtl/Snakefile \
     --configfile config_analysis.json \
     --printshellcmds \
     --latency-wait 600 \
     --jobs 999 \
     --cluster-config ${SNK_DIR}/lib/configs/config_cluster_sge.json \
     --cluster ${SNK_DIR}/lib/wrappers/cluster/sge.py \
     $1
