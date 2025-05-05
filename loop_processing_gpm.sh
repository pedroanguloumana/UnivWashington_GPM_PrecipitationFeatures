#!/bin/bash
myid=${OMPI_COMM_WORLD_RANK:-0}
size=${OMPI_COMM_WORLD_SIZE:-1}

declare -i i=0

source ~/anaconda3/etc/profile.d/conda.sh
conda activate UnivWashington_GPM_PrecipitationFeatures
REGION='H01'

for y in 2023 ; do
    for m in {1..10}; do
        if [ "$(expr $i % $size)" == "$myid" ]; then
            python /home/disk/p/pangulo/UnivWashington_GPM_PrecipitationFeatures/Process_GPM_Data.py ${REGION} ${y} ${m}
        fi
           junk=$((i++))
    done
done