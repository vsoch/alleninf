from glob import glob
import os
import pandas as pd
import numpy as np
import nibabel as nb
import numpy.linalg as npl

#code from neurosynth
def get_sphere(coords, r, vox_dims, dims):
    """ # Return all points in Allen within r mm of image coordinate. Generates a cube
    and then discards all points outside sphere. Only returns values that
    fall within the dimensions of the image."""
    r = float(r)
    # Here is how much we are going to go in each direction of the coords to have the desired radius
    xx, yy, zz = [slice(-r / vox_dims[i], r / vox_dims[i] + 0.01, 1) for i in range(len(coords))]
    # Make a cube, and cut out diagonal corners to get a sphere
    cube = np.vstack([row.ravel() for row in np.mgrid[xx, yy, zz]])
    sphere = cube[:, np.sum(np.dot(np.diag(vox_dims), cube) ** 2, 0) ** .5 <= r]
    # Now add the coordinates to put in image space
    sphere = np.round(sphere.T + coords)
    return sphere[(np.min(sphere, 1) >= 0) & (np.max(np.subtract(sphere, dims), 1) <= -1),:].astype(int)


def get_values_at_locations(nifti_file, locations, radius=None, mask_file=None,  verbose=False):
    values = []
    nii = nb.load(nifti_file)
    data = nii.get_data()
    
    if mask_file:
        mask_data = nb.load(mask_file).get_data()
        mask = np.logical_and(np.logical_not(np.isnan(mask_data)), mask_data > 0)
    else:
        if verbose:
            print "No mask provided - using implicit (not NaN, not zero) mask"
        mask = np.logical_and(np.logical_not(np.isnan(data)), data != 0)
        
    for location in locations:
        # This transforms the location from Allen into the image space, round to 1 decimal
        coord_data = [round(i) for i in nb.affines.apply_affine(npl.inv(nii.get_affine()), location)]
        # This will be true where we create our mask - all False at init
        sph_mask = (np.zeros(mask.shape) == True)
        if radius:
            sph = tuple(get_sphere(coord_data, vox_dims=nii.get_header().get_zooms(),r=radius, dims=nii.shape).T)
            # Set the voxels to True at the sphere
            sph_mask[sph] = True
        else:
            #if radius is not set use a single point
            sph_mask[coord_data[0], coord_data[1], coord_data[2]] = True
        # Create the final roi by comining the sphere and mask
        roi = np.logical_and(mask, sph_mask)
        
        # If the roi is outside of the statmap mask we should treat it as a missing value
        if np.any(roi):
            val = data[roi].mean()
        else:
            val = np.nan
        values.append(val)
    return values

def combine_expression_values(expression_values, method="average"):
    if method == "average":
        return list(np.array(expression_values).mean(axis=0))
    elif method == "pca":
        from sklearn.decomposition import TruncatedSVD
        pca = TruncatedSVD(n_components=1)
        pca.fit(np.array(expression_values))
        return list(pca.components_[0,:])
    else:
        raise Exception("Uknown method")

if __name__ == '__main__':
  print __doc__
