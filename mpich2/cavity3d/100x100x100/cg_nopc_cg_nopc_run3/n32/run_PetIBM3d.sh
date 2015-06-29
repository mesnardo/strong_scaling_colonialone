#!/bin/sh

#SBATCH --job-name="n32"
#SBATCH --output=log_summary_n32.out
#SBATCH --error=log_summary_n32.err
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH -n 32


module load mpich2/ge/gcc

PETIBM_DIR=$HOME/src/PetIBM
PETIBM3D=$PETIBM_DIR/bin/PetIBM3d

time mpirun $PETIBM3D -caseFolder . \
	-sys1_pc_type none \
	-sys2_pc_type none \
	-log_summary