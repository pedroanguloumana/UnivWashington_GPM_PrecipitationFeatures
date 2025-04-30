import argparse
import xarray as xr
from src.loading_and_extraction import *
from src.feature_statistics import *
from src.saving import *
# ---------------------------------------------------------------------------
# SECTION: PROCESSING CONSTANTS
PRECIPITATION_THRESHOLD = 1.0  # min rain rate to be considered a rainy pixel (mm/hr)
MIN_PF_SIZE_IN_PIZELS = 4      # min PF size (in pixels)

# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# SECTION: MAIN PROCESSING FUNCTION

def process(region, year, month, stats_to_compute):
    # Initalize data dictionaries
    stats_to_save = {
        'gpm_filename': [],
        'feature_id':   [],
        'is_complete':  []
    } 
    for var_name in stats_to_compute.keys():
        stats_to_save[var_name] = []
    
    # Loop over files
    files = gpm_region_files(region, year, month)

    for fi, file in enumerate(files):
        # Load GPM scenes
        scene_ds = xr.open_dataset(file).drop_vars(('start_time', 'stop_time')).squeeze('time').astype(float)

        # Identify valid, scene pixels, and those on the edge.
        # Edge-touching PFs are by identified  
        on_edge_mask = is_on_swath_edge(scene_ds)
        in_swath_mask = is_in_swath(scene_ds)
        is_complete = (in_swath_mask) & (~on_edge_mask)

        # Extract boundaries of each PF
        labelled_array = get_labelled_array(scene_ds, threshold=1.0)
        pf_slices = get_label_slices(labelled_array)

        # Loop over PFs and compute statistics
        for pf_id_m1, pf_slice in enumerate(pf_slices):

            # Extract the PF and verify its size
            pf_id = pf_id_m1 + 1
            pf_box = scene_ds.isel(pf_slice)
            pf_mask = (labelled_array.isel(pf_slice)==pf_id)
            if pf_mask.sum() < MIN_PF_SIZE_IN_PIZELS:
                continue       
            pf = pf_box.where(pf_mask, drop=True)

            # Save the computed data
            stats_to_save['gpm_filename'].append(file)
            stats_to_save['feature_id'].append(f'{pf_id:04d}')
            stats_to_save['is_complete'].append(is_complete.isel(pf_slice).all().item())

            for var_name, stat_func in stats_to_compute.items():
                stats_to_save[var_name].append(stat_func(pf))

    save_dataframe(stats_to_save, region, year, month)
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # ---------------------------------------------------------------------------
    # SECTION: PARSE ARGUMENTS
    parser = argparse.ArgumentParser(description="Parse region, year, and month inputs.")
    parser.add_argument('region', type=str, help='The region abbreviation (string input)')
    parser.add_argument('year', type=int, help='The year (integer input)')
    parser.add_argument('month', type=int, help='The month (integer input)')
    args = parser.parse_args()
    region = args.region
    year = args.year
    month = args.month
    # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------
    # SECTION: CHOOSE STATISTICS TO COMPUTE
    stats_to_compute = get_stats_dict(
        do_basic_info=True,
        do_rain_stats=True,
        do_core_stats=True
    )

    process(region, year, month, stats_to_compute)

    # ---------------------------------------------------------------------------