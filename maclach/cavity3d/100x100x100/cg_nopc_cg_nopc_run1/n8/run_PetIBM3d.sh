#!/bin/sh

#SBATCH --job-name="n8"
#SBATCH --output=log_summary_n8.out
#SBATCH --error=log_summary_n8.err
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH -n 8


module load openmpi/1.8/gcc/4.9.2/cpu

PETIBM_DIR=$HOME/src/PetIBM_maclach
PETIBM3D=$PETIBM_DIR/bin/PetIBM3d

time mpirun $PETIBM3D -caseFolder . \
	-sys1_pc_type none \
	-sys2_pc_type none \
	-log_summary
