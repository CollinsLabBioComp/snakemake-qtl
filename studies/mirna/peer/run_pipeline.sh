#!/bin/sh

## Since we aren't passing env variables, initialize env
source /home/taylorhj/.bashrc

## Activate QTL conda environment
source activate peer

## Set any necessary env variables
export SNK_DIR="/cluster/ifs/projects/collins/taylorhj/projects/snakemake-qtl"

## need to add to path to work in pipeline
export PATH="${SNK_DIR}/lib/bin/qtl_tools:$PATH"

cp ${SNK_DIR}/lib/configs/config_cluster_sge.json config_cluster.json

snakemake \
     --snakefile ${SNK_DIR}/pipelines/peer/Snakefile \
     --configfile config_analysis.json \
     --printshellcmds \
     --latency-wait 600 \
     --jobs 999 \
     --cluster-config ${SNK_DIR}/lib/configs/config_cluster_sge.json \
     --cluster ${SNK_DIR}/lib/wrappers/cluster/sge.py \
     $1

## Clean up
rm config_cluster.json
