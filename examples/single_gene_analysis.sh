#!/usr/bin/sh

# Compare map dso_0060131 with gene AKR7A3, output data table as well as results file
GENE=AKR7A3
/home/vanessa/Documents/Work/GENE_EXPRESSION/alleninf
alleninf --gene $GENE --radius 3 --data True /home/vanessa/Documents/Work/BRAINBEHAVIOR/DisorderMaps/dso_0060046_pAgF_z_FDR_0.05.nii.gz $OUTDIR/$GENE"_alleninf.tsv"

GENE=AKAP4
alleninf --gene $GENE --radius 3 --data True /home/vanessa/Documents/Work/BRAINBEHAVIOR/DisorderMaps/dso_0060131_pAgF_z_FDR_0.05.nii.gz $OUTDIR/$GENE"_alleninf.tsv"

GENE=LOC400752
alleninf --gene $GENE --radius 3 --data True /home/vanessa/Documents/Work/BRAINBEHAVIOR/DisorderMaps/dso_10933_pAgF_z_FDR_0.05.nii.gz $OUTDIR/$GENE"_alleninf.tsv"

GENE=MB
alleninf --gene $GENE --radius 3 --data True /home/vanessa/Documents/Work/BRAINBEHAVIOR/DisorderMaps/dso_1307_pAgF_z_FDR_0.05.nii.gz $OUTDIR/$GENE"_alleninf.tsv"


