#!/bin/sh

#SBATCH --job-name="n8"
#SBATCH --output=log_summary_n8.out
#SBATCH --error=log_summary_n8.err
#SBATCH --partition=short
#SBATCH --time=01:00:00
#SBATCH -n 8


module load openmpi/gcc/64/1.8

PETSC_DIR=$HOME/src/petsc/3.5.2
PETSC_ARCH=linux-openmpi-gnu-opt

PETIBM_DIR=$HOME/src/PetIBM
PETIBM3D=$PETIBM_DIR/bin/PetIBM3d

time mpirun $PETIBM3D -caseFolder . \
	-sys1_pc_type none \
	-sys2_pc_type none \
	-log_summary
