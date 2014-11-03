import os
import pandas as pd
import numpy as np
from glob import glob
import pickle

# LOADING FUNCTIONS **
def get_probe_lookup():
    return pickle.load(open("data/gene_probe_lookup.pkl","rb"))

def get_unique_genes():
    return pickle.load(open("data/unique_genes.pkl","rb"))

def get_probe_expression():
    return pd.io.pickle.read_pickle("data/probe_expression.pkl")

def get_probe_meta(probes_input="data/probes.pkl"):
    return pd.io.pickle.read_pickle(probes_input)

def get_samples(samples_input="data/samples.pkl"):
    return pd.io.pickle.read_pickle(samples_input)

# SAVING FUNCTIONS (all in pickle)
def save_probe_lookup(pickle_output="data/gene_probe_lookup.pkl"):
    """Reads in unique genes from pickle, outputs dictionary to look up probes by genes"""
    unique_genes = get_unique_genes()
    gene_lookup = get_probes_from_genes(unique_genes)
    pickle.dump(gene_lookup,open( pickle_output, "wb" ) )

def save_samples_meta(samples_csv,pickle_output="data/samples.pkl"):
    """Reads in samples.csv, outputs samples pickle"""
    samples = pd.read_csv(samples_csv)
    samples.to_pickle(pickle_output)

def save_probes_meta(probes_csv,pickle_output="data/probes.pkl"):
    """Reads in Probes.csv provided by Allen, outputs a pickle object of data"""
    probes = pd.read_csv(probes_csv,header=None)
    # I'm not totally sure about the structure/well id colnames, but we just need genes and probe ids'
    probes.columns = ["id","name","structure_id","gene","description","parent_structure_id","well_id"]
    probes.to_pickle(pickle_output)

def save_probes_expression(expression_csv,pickle_output="data/probes_expression.pkl"):
    """Reads in table of full expression (3702 columns: samples, 58K rows: probes) and saves pickle"""
    probes = pd.read_csv(expression_csv)
    tmp = [str(x) for x in range(0,3703)]
    tmp[0] = "ID"
    probes.columns = tmp
    probes.to_pickle(pickle_output)

def save_unique_genes(pickle_output="data/unique_genes.pkl"):
    probes = get_probe_meta()
    """Reads in probes meta pickle, saves list of unique genes to pickle"""
    # Now we want to parse a dictionary of probes associated with each gene
    genes = [gene for gene in probes["gene"]]
    genes = list(np.unique(genes))
    genes = [g.replace("'","") for g in genes]
    # Remove any 'na' values
    genes.pop(genes.index("na"))
    pickle.dump(genes,open( pickle_output, "wb" ) )

if __name__ == '__main__':
    print __doc__
