import pylab as plt
import numpy as np
from scipy.stats.stats import pearsonr, ttest_1samp, percentileofscore,linregress

def fixed_effects(data, labels):
    
    corcoeff, p_val = pearsonr(data[labels[0]], data[labels[1]])
    print "Pearson correlation between %s and %s across all donors is %g (two tailed p value = %g)"%(labels[0], labels[1], corcoeff, p_val)
    return corcoeff, p_val

def approximate_random_effects(data, labels, group):

    correlation_per_donor = {}
    for donor_id in set(data[group]):
        correlation_per_donor[donor_id], _, _, _, _ = linregress(list(data[labels[0]][data[group] == donor_id]),list(data[labels[1]][data[group] == donor_id]))
    average_slope = np.array(correlation_per_donor.values()).mean()
    t, p_val = ttest_1samp(correlation_per_donor.values(), 0)
    print "Averaged slope across donors = %g (t=%g, p=%g)"%(average_slope, t, p_val)    
    return average_slope, t, p_val
