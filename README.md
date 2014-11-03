alleninf
========

Compare an unthresholded statistical map of a brain with gene expression patterns from [Allen Human Brain Atlas](http://human.brain-map.org/).

Credits
------------

    Forked from https://github.com/chrisfilo/alleninf.git


Installation
------------

    pip install git+https://github.com/vsoch/alleninf.git

Usage
-----

	To query all genes in Allen Brain Human Atlas:
	usage: scripts.py [-h] [--inference_method INFERENCE_METHOD]
	                  [--probes_reduction_method PROBES_REDUCTION_METHOD]
	                  [--mask MASK] [--radius RADIUS]
	                  [--out OUTPUT_TSV_FILE ]
	                  stat_map
	
	Compare a statistical map with gene expression patterns from Allen Human Brain
	Atlas.
	
	required arguments:
	  stat_map              Unthresholded statistical map in the form of a 3D
	                        NIFTI file (.nii or .nii.gz) in MNI space.
	
	optional arguments:
	  -h, --help            show this help message and exit

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
    $ alleninf Tstat.nii.gz --mask mask.nii.gz --out outfile.tsv

