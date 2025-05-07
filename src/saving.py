import pandas as pd
from functools import partial
from src.feature_statistics import *

def get_stats_dict(do_basic_info, do_rain_stats, do_core_stats):
    stats_to_compute = dict()
    if do_basic_info:
        stats_to_compute.update(
            {
                'observation_time': observation_time,
                'mean_latitude': mean_latitude,
                'mean_longitude': mean_longitude,
                'precipitation_centroid_latitude': precipitation_centroid_latitude,
                'precipitation_centoid_longitude': precipitation_centroid_longitude, 
            }
        )

    if do_rain_stats:
        stats_to_compute.update(
            {
                'num_pixels': num_pixels,
                'num_convective_pixels': num_conv_pixels,
                'num_stratiform_pixels': num_strat_pixels,
                'total_precip': total_precip,
                'total_convective_precip': total_conv_precip,
                'total_stratiform_precip': total_strat_precip,
                'max_precip': max_precip,
                'gini_index': gini,
            }
        )
    if do_core_stats:
        stats_to_compute.update(
            {
                'largest_2mmhr_cluster_rain':  lambda x: largest_rain_cluster_precip(x, rain_thresh=2),
                'largest_5mmhr_cluster_rain':  lambda x: largest_rain_cluster_precip(x, rain_thresh=5),
                'largest_15mmhr_cluster_rain': lambda x: largest_rain_cluster_precip(x, rain_thresh=15),
                'largest_20mmhr_cluster_rain': lambda x: largest_rain_cluster_precip(x, rain_thresh=20),
                'largest_convective_cluster_rain': largest_convective_cluster_precip
            }
        )



    return stats_to_compute

def save_dataframe(database_dict, region, year, month):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(database_dict)
    
    # Construct the directory path
    path_to_save = f'/home/disk/tc/pangulo/gpm_precip_features/{region}/'
    
    # Ensure the directory exists
    os.makedirs(path_to_save, exist_ok=True)
    
    # Construct the full filename
    filename = f'{path_to_save}gpm_pf_stats.{region}.{year}.{month:02d}.csv'
    
    # Check if the file exists
    if os.path.exists(filename):
        # Append without writing the header
        raise RuntimeError("append mode deprecated")
        df.to_csv(filename, mode='a', header=False, index=False)
        print(f"Appended data to existing file: {filename}")
    else:
        # Write the file with the header
        df.to_csv(filename, index=False)
        print(f"Created new file and saved data: {filename}")