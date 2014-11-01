import os
import pandas as pd
import numpy as np
from glob import glob
import pickle
from api import get_genes

def allen_probes_csv_to_pickle(probes_csv, pickle_output="data/probes.pkl"):
    """Reads in Allen Brain Atlas probes.csv file, outputs a pickle data table of probes"""
    probes = pd.read_csv(probes_csv,header=None)
    # I'm not totally sure about the structure/well id colnames, but we just need genes and probe ids'
    probes.columns = ["id","name","structure_id","gene","description","parent_structure_id","well_id"]
    probes.to_pickle(pickle_complete_output)

def allen_get_unique_genes_pickle(probes_input="data/probes.pkl", pickle_output="data/unique_genes.pkl"):
    """Reads in Allen Brain Atlas probes pickle file, outputs unique genes pickle"""
    probes = pd.io.pickle.read_pickle(probes_input)
    # Now we want to parse a dictionary of probes associated with each gene
    genes = [gene for gene in probes["gene"]]
    genes = list(np.unique(genes))
    genes = [g.replace("'","") for g in genes]
    # Remove any 'na' values
    genes.pop(genes.index("na"))
    pickle.dump(genes,open( pickle_output, "wb" ) )

def allen_make_gene_probe_lookup_pickle(pickle_output="data/gene_probe_lookup.pkl")
    """Reads in Allen Brain Atlas unique genes pickle file, outputs gene lookup pickle"""
    unique_genes = get_genes()
    gene_lookup = get_probes_from_genes(unique_genes)
    # This would take forever
    #ids = [theid for theid in probes["id"]]
    #print "Saving pickle list to file... this can take some time."
    #probe_list = {gene:{probe[1]["id"]:probe[1]["name"] for probe in probes.iterrows() if probe[1]["gene"] == gene} for gene in genes}
    pickle.dump(gene_lookup,open( pickle_output, "wb" ) )


# TODO: Update to save to pickle, I don't have hd5 headers and can't get to work'
def allen_csv_to_hdf(donors_dir, hdf_output='data/microarray_expression.h5'):
    """Takes a directory with one subdirectory for each donor containing a
    SampleAnnot.csv and MicroarrayExpression.csv files. The output is a 
    compressed HDF5 file containing concatenated wells x gene probes table."""
    
    donor_ids = [p.split(os.sep)[-1] for p in glob(os.path.join(data_dir, "*"))]

    for donor_id in donor_ids:
        print "adding donor %s"%donor_id
        sample_locations = pd.read_csv(os.path.join(data_dir, 
                donor_id, 'SampleAnnot.csv'))
        df = pd.DataFrame({"well_id":list(sample_locations.well_id)})
        expression_data = pd.read_csv(os.path.join(data_dir, 
                donor_id, 
                'MicroarrayExpression.csv'), 
            header=None, index_col=0, dtype=np.float32)
        expression_data.columns = range(expression_data.shape[1])
        df = pd.concat([df, expression_data.T], axis=1, ignore_index=False)
        df.set_index("well_id", inplace=True)
        df = df.transpose()
        
        df.columns = ["well_id_" + str(int(c)) for c in df.columns]
        df.index = [int(c) for c in df.index]
        df.index.name = 'probe_id'
        df.to_hdf(hdf_output, donor_id, mode="a", format='table', complevel=9, complib='blosc')

if __name__ == '__main__':
    data_dir='../../../papers/beyond_blobs/data/donors'
    allen_csv_to_hdf(data_dir)
