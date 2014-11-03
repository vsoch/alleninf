#!/usr/bin/env python
import argparse
import os
import numpy as np
import pandas as pd
import nibabel as nb

import alleninf.api
from alleninf.utils import get_probe_lookup, get_probe_expression, get_samples
from alleninf.analysis import fixed_effects, approximate_random_effects
from alleninf.data import combine_expression_values, get_values_at_locations

def nifti_file(string):
    if not os.path.exists(string):
        msg = "%r does not exist" % string
        raise argparse.ArgumentTypeError(msg)
    try:
        nii = nb.load(string)
    except IOError as e:
        raise argparse.ArgumentTypeError(str(e))
    except:
        msg = "%r is not a nifti file" % string
        raise argparse.ArgumentTypeError(msg)
    else:
        if len(nii.shape) == 4 and nii.shape[3] > 1:
            msg = "%r is four dimensional" % string
            raise argparse.ArgumentTypeError(msg)
    return string


def main():
    parser = argparse.ArgumentParser(
        description="Compare a statistical map with gene expression patterns from Allen Human Brain Atlas.")
    parser.add_argument("stat_map", help="Unthresholded statistical map in the form of a 3D NIFTI file (.nii or .nii.gz) in MNI space.", type=nifti_file)
    parser.add_argument("--inference_method", help="Which model to use: fixed - fixed effects, approximate_random - approximate random effects (default), ",default="approximate_random")
    parser.add_argument("--probes_reduction_method", help="How to combine multiple probes: average (default) or pca - use first principal component (requires scikit-learn).",default="average")
    parser.add_argument("--mask", help="Explicit mask for the analysis in the form of a 3D NIFTI file (.nii or .nii.gz) in the same space and dimensionality as the stat_map. If not specified an implicit mask (non zero and non NaN voxels) will be used.",type=nifti_file)
    parser.add_argument("--radius", help="Radius in mm of of the sphere used to average statistical values at the location of each probe (default: 4mm).",default=4, type=float)
    parser.add_argument("out", help="Full path to output file",default="alleninf_analaysis_output.tsv", type=str)
    parser.add_argument("--gene", help="Perform analysis for a specific gene only.",default=None, type=str)
    parser.add_argument("--data", help="Export data for all genes: a csv with expression values.",default=False, type=bool)

    args = parser.parse_args()

    # Get complete list of probes assigned to each gene
    probes_dict = get_probe_lookup()

    # If we are only querying for one gene:
    if args.gene:
      print "Performing analysis with gene %s" % (str(args.gene))
      tmp = probes_dict[gene]
      probes_dict = {gene:tmp}
    else: 
      print "Found %s genes each with assigned probes." % (len(probes_dict))

    # Get complete samples meta info, and corrected mni coordinates
    samples = get_samples()
    mni_coordinates = list(samples[["corrected_mni_x","corrected_mni_y","corrected_mni_z"]].itertuples(index=False))
    donors = list(samples["id"])

    # Get all expression values
    print "Loading expression from file..."
    expression = get_probe_expression()

    # Get MNI coordinates of nifti file
    print "Getting values in nifti map at Allen samples locations..."
    nifti_values = get_values_at_locations(args.stat_map, mni_coordinates, mask_file=args.mask, radius=args.radius, verbose=True)

    # We will save fixed effects corcoeff, p value, and approx. random effects
    res = []

    # If the user wants to output data
    if args.data:  output_data = dict()

    # Combine expression values across probes
    for gene,probes in probes_dict.iteritems():
      print "Combining expression values for gene %s" % (gene)
      # Get combined expression values
      expression_values = expression[expression["ID"].isin(probes.keys())]
      expression_values = expression_values.drop('ID', 1)
      combined_expression_values = combine_expression_values(expression_values, method=args.probes_reduction_method)
    
      # Put results into data frame
      names = ["NIFTI values", "%s expression" % gene, "Donor ID"]
      data = pd.DataFrame(np.transpose(np.array([nifti_values, combined_expression_values, donors])), columns=names)
      data = data.convert_objects(convert_numeric=True)
      length_before = len(data)
      data.dropna(axis=0, inplace=True)
      nans = length_before - len(data)
      # This coverage is an issue
      if nans > 0:
        print "%s wells fall outside of the mask" % nans

      if args.inference_method == "fixed":
        print "Performing fixed effect analysis"
        corcoeff, p_val = fixed_effects(data, names)
        result = [gene,str(len(probes)),",".join(probes.values()),corcoeff,p_val]
        res.append(result)

      if args.inference_method == "approximate_random":
        print "Performing approximate random effect analysis"
        average_slope, t, p_val = approximate_random_effects(data, names, "Donor ID")
        result = [gene,str(len(probes)),",".join(probes.values()),t,p_val,average_slope]
        res.append(result)

    # If the user wants to output data
    if args.data: output_data[gene] = data

    if args.inference_method == "approximate_random":
      result = pd.DataFrame(res,columns=["gene","probe_count","probes","t","p_value","average_slope"])
    if args.inference_method == "fixed":
      result = pd.DataFrame(res,columns=["gene","probe_count","probes","corrcoeff","p_value"])
    
    print "Saving result to output file " + str(args.out) + "..."
    result.to_csv(args.out,sep="\t")
    if args.data:
      output_file = "%s/%s_%s_alleninf.csv" % (os.path.dirname(args.out),gene,os.path.basename(re.sub(".nii.gz|.nii.gz|.img","",args.stat_map)))
      print "Saving raw data files for all genes in %s" %(output_file)
      output_data[gene].to_csv(output_file)

if __name__ == '__main__':
    main()
