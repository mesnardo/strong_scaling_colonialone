#!/bin/sh

#SBATCH --job-name="n128"
#SBATCH --output=log_summary_n128.out
#SBATCH --error=log_summary_n128.err
#SBATCH --partition=short
#SBATCH --time=00:15:00
#SBATCH -n 128


module load openmpi/1.8/gcc/4.9.2

PETSC_DIR=$HOME/src/petsc/3.5.2
PETSC_ARCH=linux-openmpi-1.8-gcc-4.9.2-opt

PETIBM_DIR=$HOME/src/PetIBM
PETIBM3D=$PETIBM_DIR/$PETSC_ARCH/PetIBM3d

time mpirun $PETIBM3D -caseFolder . \
	-sys1_pc_type none \
	-sys2_pc_type none \
	-log_summary
