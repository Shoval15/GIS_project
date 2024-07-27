import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd

def create_heat(merged_data, not_allocated_buildings, gardens_gdf):
    # Create a plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot non-allocated buildings in red
    not_allocated_buildings.plot(ax=ax, color='red', alpha=0.7, label='Not Allocated')

    # Plot allocated buildings in green
    merged_data.plot(ax=ax, color='green', alpha=0.7, label='Allocated')

    # Plot gardens
    gardens_gdf.plot(ax=ax, color='blue', alpha=0.5, markersize=gardens_gdf['capacity']/10, label='Gardens')

    # Add labels, title, etc.
    plt.title('Building Allocation to Community Gardens')
    plt.legend()

    # Adjust the plot to show the full extent of the data
    plt.tight_layout()

    plt.show()