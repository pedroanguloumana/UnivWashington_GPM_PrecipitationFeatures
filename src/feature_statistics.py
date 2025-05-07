import numpy as np
import os
import xarray as xr

from scipy.ndimage import label

def observation_time(ds, format='%Y%m%d_%H:%M:%S'):
    obs_time_string = ds.time.dt.strftime(format).item()
    return obs_time_string

def mean_latitude(ds):
    mean_lat = ds.lat.where(ds.near_surf_rain>0).mean().item()
    return mean_lat

def mean_longitude(ds):
    mean_lon = ds.lon.where(ds.near_surf_rain > 0).mean().item()
    return mean_lon

def precipitation_centroid_latitude(ds):
    lat = ds.lat.weighted(ds.near_surf_rain.fillna(0)).mean().item()
    return lat

def precipitation_centroid_longitude(ds):
    lon = ds.lon.weighted(ds.near_surf_rain.fillna(0)).mean().item()
    return lon

def num_pixels(ds):
    N = (ds.near_surf_rain>0).sum().item()
    return N

def num_conv_pixels(ds):
    N = ((ds.near_surf_rain>0)&(ds.rain_type==2)).sum().item()
    return N

def num_strat_pixels(ds):
    N = ((ds.near_surf_rain>0)&(ds.rain_type==1)).sum().item()
    return N

def num_rain_thresh_pixels(ds, rain_thresh=0):
    N = (ds.near_surf_rain>rain_thresh).sum().item()
    return N

def total_precip(ds):
    pr = ds.near_surf_rain.sum().item()
    return pr

def total_conv_precip(ds):
    pr = ds.near_surf_rain.where(ds.rain_type==2).sum().item()
    return pr

def total_strat_precip(ds):
    pr = ds.near_surf_rain.where(ds.rain_type==1).sum().item()
    return pr

def max_precip(ds):
    pr = ds.near_surf_rain.max().item()
    return pr

def largest_cluster_mask(data_to_segment, connectivity):
    data_to_segment = (data_to_segment)  # for historical reasons
    # Label connected components in the mask
    if connectivity==8:
        structure = [[1,1,1],[1,1,1],[1,1,1]]
    elif connectivity==4:
        structure = [[0,1,0],[1,1,1],[0,1,0]]

    labeled, n_components = label(data_to_segment.data, structure=structure)
    if n_components == 0:
        mask = np.zeros_like(data_to_segment.data, dtype=bool)
    else:
        sizes = np.bincount(labeled.ravel())
        sizes[0] = 0
        largest_label = sizes.argmax()
        mask = (labeled == largest_label)

    mask_da = xr.DataArray(
        mask,
        coords=data_to_segment.coords,
        dims=data_to_segment.dims
    )
    return mask_da

def largest_rain_cluster_precip(ds, rain_thresh):
    precip = ds.near_surf_rain
    rainy_mask = (precip >= rain_thresh)
    largest_cluster = largest_cluster_mask(rainy_mask, connectivity=8)
    return precip.where(largest_cluster, drop=True).sum().item()

def largest_convective_cluster_precip(ds):
    precip = ds.near_surf_rain
    convective_mask = (ds.rain_type==2)
    largest_cluster = largest_cluster_mask(convective_mask, connectivity=8)
    return precip.where(largest_cluster, drop=True).sum().item()

def gini(ds):
    x = ds.near_surf_rain.data.ravel()
    x = x[~np.isnan(x)]

    if x.ndim != 1:
        raise ValueError("Input must be 1-D")

    if np.any(x < 0):
        raise ValueError("Values must be non-negative")

    if np.all(x == 0):
        return 0.0                       # undefined mathematically, but sensible

    x_sorted = np.sort(x)
    n = x_sorted.size
    cumindex = np.arange(1, n + 1)       # 1 … n

    return (np.sum((2 * cumindex - n - 1) * x_sorted) /
            (n * x_sorted.sum()))
    