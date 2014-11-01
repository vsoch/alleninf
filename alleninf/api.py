import json
import urllib2
import os
#from tables import open_file deleting because I don't have tables'
import pandas as pd
import numpy as np
import pickle
from alleninf.datasets import fetch_microarray_expression

api_url = "http://api.brain-map.org/api/v2/data/query.json"

# Here we will load all probes assigned to each gene from the Allen Brain Atlas, saved in pickle object
def get_all_probes():
    probes = pd.io.pickle.read_pickle("data/gene_probe_lookup.pkl")
    return probes

# Load list of unique genes
def get_genes():
    return pickle.load(open("data/unique_genes.pkl","rb"))

def get_genes_lookup():
    return pickle.load(open("data/gene_probe_lookup.pkl",'rb'))

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
      print "Querying for gene " + gene + ": " + str(g) + " of " + str(len(gene_names))
      api_query = "?criteria=model::Probe"
      api_query += ",rma::criteria,[probe_type$eq'DNA']"
      api_query += ",products[abbreviation$eq'HumanMA']"
      api_query += ",gene[acronym$eq%s]" % (','.join(gene))
      api_query += ",rma::options[only$eq'probes.id','name']"
      data = json.load(urllib2.urlopen(api_url + api_query))
      d = {probe['id']: probe['name'] for probe in data['msg']}
      if d:
        probe_lookup[gene] = d
      else:
        probe_notfound.append(gene)

    if len(notfound >0):
      print "Genes not found during analysis: " + str(notfound)
      print "See http://help.brain-map.org/download/attachments/2818165/HBA_ISH_GeneList.pdf?version=1&modificationDate=1348783035873 for list of available genes."

    return probe_lookup


def get_expression_values_from_probe_ids(probe_ids, restapi=True):
    if restapi:
        return get_expression_values_from_probe_ids_restapi(probe_ids)
    else:
        return get_expression_values_from_probe_ids_hdf(probe_ids)


def get_expression_values_from_probe_ids_restapi(probe_ids):
    if not isinstance(probe_ids, list):
        probe_ids = [probe_ids]
    # in case there are white spaces in gene names
    probe_ids = ["'%s'" % probe_id for probe_id in probe_ids]

    api_query = "?criteria=service::human_microarray_expression[probes$in%s]" % (
        ','.join(probe_ids))
    data = json.load(urllib2.urlopen(api_url + api_query))

    expression_values = [[float(expression_value) for expression_value in data[
        "msg"]["probes"][i]["expression_level"]] for i in range(len(probe_ids))]
    well_ids = [sample["sample"]["well"] for sample in data["msg"]["samples"]]
    donor_names = [sample["donor"]["name"]
                   for sample in data["msg"]["samples"]]
    well_coordinates = [sample["sample"]["mri"]
                        for sample in data["msg"]["samples"]]

    return expression_values, well_ids, donor_names


def get_expression_values_from_probe_ids_hdf(probe_ids):
    files = fetch_microarray_expression()
    hdf_file = files.microarray_expression

    h_handle = open_file(hdf_file, "r")
    donors = [g._v_name for g in list(h_handle.walkGroups("/"))[1:]]
    h_handle.close()

    probe_ids = ["'%s'" % probe_id for probe_id in probe_ids]
    where_query = "index in [%s]" % (",".join(probe_ids))

    expression_values = []
    well_ids = []
    donor_names = []
    for donor in donors:
        df = pd.read_hdf(hdf_file, donor, where=where_query, close=True)
        well_ids += [int(col[len("well_id_"):]) for col in df.columns]
        donor_names += [donor, ] * len(df.columns)
        expression_values.append(np.array(df))

    expression_values = list(np.concatenate(expression_values, axis=1))
    return expression_values, well_ids, donor_names


def get_mni_coordinates_from_wells(well_ids):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    frame = pd.read_csv(os.path.join(
        package_directory, "data", "corrected_mni_coordinates.csv"), header=0, index_col=0)

    return list(frame.ix[well_ids].itertuples(index=False))

if __name__ == '__main__':
    probes_dict = get_probes_from_genes("HTR1A")
    expression_values, well_ids, donor_names = get_expression_values_from_probe_ids_hdf(
        probes_dict.keys())
    print get_mni_coordinates_from_wells(well_ids)
