#!/bin/sh

#SBATCH --job-name="n64"
#SBATCH --output=log_summary_n64.out
#SBATCH --error=log_summary_n64.err
#SBATCH --partition=short
#SBATCH --time=00:15:00
#SBATCH -n 64


module load mpich/3.1.4

PETSC_DIR=$HOME/src/petsc/3.5.2
PETSC_ARCH=linux-mpich-3.1.4-gnu-opt

PETIBM_DIR=$HOME/src/PetIBM
PETIBM3D=$PETIBM_DIR/bin/PetIBM3d

time mpirun $PETIBM3D -caseFolder . \
	-sys1_pc_type none \
	-sys2_pc_type none \
	-log_summary
