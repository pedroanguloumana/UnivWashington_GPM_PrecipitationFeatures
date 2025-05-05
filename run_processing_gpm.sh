#!/bin/bash
#$ -N  h01_2023   # Job name
#$ -e /home/disk/p/pangulo/UnivWashington_GPM_PrecipitationFeatures/job_scripts # Error file
#$ -o /home/disk/p/pangulo/UnivWashington_GPM_PrecipitationFeatures/job_scripts # Output file

cd /home/disk/p/pangulo/UnivWashington_GPM_PrecipitationFeatures/
mpirun -np $NSLOTS /bin/bash -c loop_processing_gpm.sh