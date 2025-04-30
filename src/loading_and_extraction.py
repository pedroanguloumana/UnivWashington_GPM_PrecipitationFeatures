from glob import glob
import os
import numpy as np
from scipy.ndimage import label, find_objects, binary_dilation



def gpm_region_files(region, year, month):
    '''
    Returns sorted list of GPM/TRMM files
    '''
    if year >=2014:
        base_path = f'/home/disk/archive3/gpm/v07/{region}/interp_data/{year}/{month:02d}/'
    elif year <=2013:
        base_path = f'/home/disk/archive3/trmm/v07/{region}/interp_data/{year}/{month:02d}/'
    assert(os.path.isdir(base_path))
    file_list = sorted(glob(base_path+'*.nc'))
    assert(len(file_list)>0)
    return file_list

def get_labelled_array(scene_ds, threshold):
    '''
    Returns array with integer labels of features. 
    Basically applies scipy.ndimage.label to GPM snapshot
    '''
    structure = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ], dtype=int)
    raining_mask = (scene_ds.near_surf_rain>=threshold).squeeze()
    labelled_array, _ = label(raining_mask.values, structure=structure)
    # conversion to xarray object for easier indexing
    labelled_array = scene_ds.swath.copy(data=labelled_array) 
    return labelled_array

def get_label_slices(labelled_array):
    slices = find_objects(labelled_array)
    # this is the correct order of coords
    pf_slices = [{'lat': s[0], 'lon': s[1]} for s in slices]
    return pf_slices

def is_in_swath(scene_ds):
    # Instead of the onboard swath variable, I will use NaN-valued precip to find the edge of the swath
    mask = np.logical_not(np.isnan(scene_ds.near_surf_rain))
    return mask

def is_on_swath_edge(scene_ds):
    in_swath = is_in_swath(scene_ds)
    not_in_swath = np.logical_not(in_swath)
    dilated_out_swath = binary_dilation(not_in_swath)
    edge = in_swath & dilated_out_swath
    return edge





