#!/usr/bin/env python
import argparse
import os
import numpy as np
import pandas as pd
import nibabel as nb

from alleninf.api import get_probes_from_genes,get_genes_lookup,get_expression_values_from_probe_ids,get_mni_coordinates_from_wells
from alleninf.data import get_values_at_locations, combine_expression_values
from alleninf.analysis import fixed_effects, approximate_random_effects, bayesian_random_effects


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
    parser.add_argument(
        "stat_map", help="Unthresholded statistical map in the form of a 3D NIFTI file (.nii or .nii.gz) in MNI space.", type=nifti_file)
    parser.add_argument("gene_name", help="Name of the gene you want to compare your map with. For list of all available genes see: "
                        "http://help.brain-map.org/download/attachments/2818165/HBA_ISH_GeneList.pdf?version=1&modificationDate=1348783035873.",
                        type=str)
    parser.add_argument("all_genes", help="True if you want to compare statistical map with all 29K genes in the atlas",type=bool)
    parser.add_argument("--inference_method", help="Which model to use: fixed - fixed effects, approximate_random - approximate random effects (default), "
                        "bayesian_random - Bayesian hierarchical model (requires PyMC3).",
                        default="approximate_random")
    parser.add_argument("--n_samples", help="(Bayesian hierarchical model) Number of samples for MCMC model estimation (default 2000).",
                        default=2000, type=int)
    parser.add_argument("--n_burnin", help="(Bayesian hierarchical model) How many of the first samples to discard (default 500).",
                        default=500, type=float)
    parser.add_argument("--probes_reduction_method", help="How to combine multiple probes: average (default) or pca - use first principal component (requires scikit-learn).",
                        default="average")
    parser.add_argument("--mask", help="Explicit mask for the analysis in the form of a 3D NIFTI file (.nii or .nii.gz) in the same space and "
                        "dimensionality as the stat_map. If not specified an implicit mask (non zero and non NaN voxels) will be used.",
                        type=nifti_file)
    parser.add_argument("--radius", help="Radius in mm of of the sphere used to average statistical values at the location of each probe (default: 4mm).",
                        default=4, type=float)
    parser.add_argument("--probe_exclusion_keyword", help="If the probe name includes this string the probe will not be used.",
                        type=str)

    args = parser.parse_args()

    if args.all_genes:
      # Load gene lookup table we have saved
      probes_dict = get_genes_lookup()
      print "Found %s genes." % (len(probes_dict))
    else:
      # Here is analysis for specific subset of genes
      print "Fetching probe ids for gene %s" % args.gene_name
      probes_dict = get_probes_from_genes(args.gene_name)
      print "Found %s probes: %s" % (len(probes_dict), ", ".join(probes_dict.values()))

    # TODO: STOPPED AT THIS POINT - still creating data object with ALL THE GENES :)
    # TODO: Need to test this - need to fix for > 1 gene
    # If we want to remove any of the genes in the set from the analysis
    if args.probe_exclusion_keyword:
        probes_dict = {probe_id: probe_name for (probe_id, probe_name) in probes_dict.iteritems() if not args.probe_exclusion_keyword in probe_name}
        print "Probes after applying exclusion cryterion: %s" % (", ".join(probes_dict.values()))

    print "Fetching expression values for probes %s" % (", ".join(probes_dict.values()))
    expression_values, well_ids, donor_names = get_expression_values_from_probe_ids(
        probes_dict.keys())
    print "Found data from %s wells sampled across %s donors" % (len(well_ids), len(set(donor_names)))

    print "Combining information from selected probes"
    combined_expression_values = combine_expression_values(
        expression_values, method=args.probes_reduction_method)

    print "Translating locations of the wells to MNI space"
    mni_coordinates = get_mni_coordinates_from_wells(well_ids)

    print "Checking values of the provided NIFTI file at well locations"
    nifti_values = get_values_at_locations(
        args.stat_map, mni_coordinates, mask_file=args.mask, radius=args.radius, verbose=True)

    # preparing the data frame
    names = ["NIFTI values", "%s expression" % args.gene_name, "donor ID"]
    data = pd.DataFrame(np.array(
        [nifti_values, combined_expression_values, donor_names]).T, columns=names)
    data = data.convert_objects(convert_numeric=True)
    len_before = len(data)
    data.dropna(axis=0, inplace=True)
    nans = len_before - len(data)
    if nans > 0:
        print "%s wells fall outside of the mask" % nans

    if args.inference_method == "fixed":
        print "Performing fixed effect analysis"
        fixed_effects(data, ["NIFTI values", "%s expression" % args.gene_name])

    if args.inference_method == "approximate_random":
        print "Performing approximate random effect analysis"
        approximate_random_effects(
            data, ["NIFTI values", "%s expression" % args.gene_name], "donor ID")

    if args.inference_method == "bayesian_random":
        print "Fitting Bayesian hierarchical model"
        bayesian_random_effects(
            data, ["NIFTI values", "%s expression" % args.gene_name], "donor ID", args.n_samples, args.n_burnin)


if __name__ == '__main__':
    main()
