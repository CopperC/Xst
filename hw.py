import tkinter as tk
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# Mapping of header values to more descriptive labels
header_labels = {
    'degT': 'Wind Direction (degrees)',
    'm/s': 'Wind Speed (m/s)',
    'm': 'Wave Height (meters)',
    'sec': 'Wave Period (seconds)',
    'hPa': 'Pressure (hPa)',
    'degC': 'Temperature (Celsius)',
    'nmi': 'Visibility (nautical miles)',
    'ft': 'Tide (feet)'
}

# Function to fetch buoy data
def fetch_buoy_data(station_id="46089"):
    try:
        # NDBC API endpoint for the specified buoy station
        api_url = f"https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt"
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = []
        lines = response.text.splitlines()
        header = lines[1].split()  # Get the header line
        print(f"Header: {header}")  # Debugging statement
        
        for line in lines[2:]:  # Skip the header lines
            parts = line.split()
            if len(parts) > 5:  # Ensure there are enough columns
                try:
                    time_str = f"{parts[0]}-{parts[1]}-{parts[2]}T{parts[3]}:{parts[4]}:00"
                    time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                    entry = {'time': time}
                    for i, column in enumerate(header[5:], start=5):
                        if parts[i] != 'MM':  # Check for missing values
                            entry[column] = float(parts[i])
                        else:
                            entry[column] = np.nan  # Use NaN for missing values
                    data.append(entry)
                except ValueError as ve:
                    print(f"ValueError: {ve} for line: {line}")  # Debugging statement
        
        # Filter data for the last 12 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=12)
        filtered_data = [entry for entry in data if start_time <= entry['time'] <= end_time]
        
        return filtered_data, header[5:]
    except Exception as e:
        print(f"Error fetching buoy data: {e}")
        return [], []

# Function to plot buoy data
def plot_buoy_data(data, column, station_id):
    try:
        values = [entry[column] for entry in data if not np.isnan(entry[column])]
        times = [entry['time'] for entry in data if not np.isnan(entry[column])]
        
        if not values:
            print(f"No data available for column: {column}")
            return False
        
        # Calculate the median value
        median_value = np.median(values)

        plt.figure(figsize=(10, 5))
        plt.plot(times, values, marker='o', label=column)
        plt.axhline(y=median_value, color='r', linestyle='--', label=f'Median {column}: {median_value:.2f}')
        plt.title(f'Buoy Data - Station {station_id} (Last 12 Hours) - {column}')
        plt.xlabel('Time')
        
        # Use descriptive label for y-axis if available
        ylabel = header_labels.get(column, column)
        plt.ylabel(ylabel)
        
        plt.legend()
        plt.grid(True)
        plt.savefig(f'buoy_data_{station_id}_{column}.png')  # Save the plot to a file
        plt.close()
        return True
    except Exception as e:
        print(f"Error plotting buoy data: {e}")
        return False

# Function to update the plot based on selected column
def update_plot(selected_column, station_id):
    data, _ = fetch_buoy_data(station_id)
    return plot_buoy_data(data, selected_column, station_id)

# Main function
def main():
    station_id = "46029"  # Change this to the desired station ID
    data, columns = fetch_buoy_data(station_id)

    if not columns:
        print("No data available to plot.")
        return

    no_data_columns = []

    # Simulate user selection and plot update
    for column in columns:
        if not update_plot(column, station_id):
            no_data_columns.append(column)
        else:
            print(f"Plot saved for column: {column}")

    if no_data_columns:
        print("\nThe following columns were not plotted due to no data being available:")
        for column in no_data_columns:
            print(f"- {column}")

if __name__ == "__main__":
    main()
