#!/bin/sh -l

export LDIR=$LOCALDIR/$SLURM_JOBID

mkdir -p $LDIR

cd $LDIR

cp $SLURM_SUBMIT_DIR/* .

module load turbomole/7.02
x2t linker.xyz > coord
uff
t2x -c > final.xyz

cp -r $LDIR/* $SLURM_SUBMIT_DIR/
rm -fR $LDIR 
