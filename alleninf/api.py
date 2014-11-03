import json
import urllib2
import os
import pandas as pd
import numpy as np
import pickle

api_url = "http://api.brain-map.org/api/v2/data/query.json"

# Here is if we want to get a set of probes from genes, querying the atlas
def get_probes_from_genes(gene_names):
    if not isinstance(gene_names, list):
        gene_names = [gene_names]
    # in case there are white spaces in gene names
    gene_names = ["'%s'" % gene_name for gene_name in gene_names]
    
    probe_lookup = dict()
    probe_notfound = []
    # We need to download each gene separately
    for g in range(0,len(gene_names)):
      gene = gene_names[g]
      api_query = "?criteria=model::Probe"
      api_query += ",rma::criteria,[probe_type$eq'DNA']"
      api_query += ",products[abbreviation$eq'HumanMA']"
      api_query += ",gene[acronym$eq%s]" % (gene)
      api_query += ",rma::options[only$eq'probes.id','name']"
      data = json.load(urllib2.urlopen(api_url + api_query))
      d = {probe['id']: probe['name'] for probe in data['msg']}
      if d:
        probe_lookup[gene.strip("'")] = d
        print "Found gene " + gene + ": " + str(g) + " of " + str(len(gene_names))
      else:
        probe_notfound.append(gene)

    if len(notfound >0):
      print "Genes not found during analysis: " + str(notfound)
      print "See http://help.brain-map.org/download/attachments/2818165/HBA_ISH_GeneList.pdf?version=1&modificationDate=1348783035873 for list of available genes."

    return probe_lookup

if __name__ == '__main__':
    probes_dict = get_probes_from_genes("HTR1A")
    expression_values, well_ids, donor_names = get_expression_values_from_probe_ids_hdf(
        probes_dict.keys())
    print get_mni_coordinates_from_wells(well_ids)
