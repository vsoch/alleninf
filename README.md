alleninf
========

Compare an unthresholded statistical map of a brain with gene expression patterns from [Allen Human Brain Atlas](http://human.brain-map.org/).

Credits
------------

    Forked from https://github.com/chrisfilo/alleninf.git


Installation
------------

    git clone https://github.com/vsoch/alleninf.git
    cd alleninf/alleninf
    wget https://www.dropbox.com/s/se9bn2rd1glbzqu/data_unzip_me.zip?dl=1 -O data_unzip_me.zip
    unzip alleninf/alleninf/data_unzip_me.zip
    cd ..
    sudo python setup.py install

Usage
-----

	To query all genes in Allen Brain Human Atlas:
	usage: scripts.py [-h] [--inference_method INFERENCE_METHOD]
	                  [--probes_reduction_method PROBES_REDUCTION_METHOD]
	                  [--mask MASK] [--radius RADIUS]
	                  [--gene GENE ] [ --data BOOLEAN ]
	                  stat_map out
	
	Compare a statistical map with gene expression patterns from Allen Human Brain
	Atlas.
	
	required arguments:
	  stat_map              Unthresholded statistical map in the form of a 3D
	                        NIFTI file (.nii or .nii.gz) in MNI space.

	  out                   Full path of output file for result (AKR7A3_alleninf.tsv).
                                The basename will be used for the data file, if specified True
	
	optional arguments:
	  -h, --help            show this help message and exit

	  --gene                Perform analysis for only one gene

	  --data                If True, output data file with gene expression and map values

	  --inference_method INFERENCE_METHOD
	                        Which model to use: fixed - fixed effects,
	                        approximate_random - approximate random effects
	                        (default)

	  --probes_reduction_method PROBES_REDUCTION_METHOD
	                        How to combine multiple probes: average (default) or
	                        pca - use first principal component (requires scikit-
	                        learn).
	  --mask MASK           Explicit mask for the analysis in the form of a 3D
	                        NIFTI file (.nii or .nii.gz) in the same space and
	                        dimensionality as the stat_map. If not specified an
	                        implicit mask (non zero and non NaN voxels) will be
	                        used.
	  --radius RADIUS       Radius in mm of of the sphere used to average
	                        statistical values at the location of each probe
	                        (default: 4mm).
	  --out OUTPUT_TSV_FILE
	                        Full path to tab separated value file for output


Example
-------

    # Querying for a single gene
    $ alleninf --gene $GENE --radius 3 --data True dso_1307_pAgF_z_FDR_0.05.nii.gz $OUTDIR/$GENE"_alleninf.tsv"
    Performing analysis with gene MB
    Loading expression from file...
    Getting values in nifti map at Allen samples locations...
    No mask provided - using implicit (not NaN, not zero) mask
    Combining expression values for gene MB
    3410 wells fall outside of the mask
    Performing approximate random effect analysis
    Averaged slope across donors = -0.105336 (t=-18.5487, p=8.38119e-06)
    Saving result to output file /home/vanessa/Documents/Work/GENE_EXPRESSION/alleninf/MB_alleninf.tsv...
    Saving raw data files for all genes in /home/vanessa/Documents/Work/GENE_EXPRESSION/alleninf/MB_dso_1307_pAgF_z_FDR_0.05_alleninf.csv
