# UK Flood Monitoring Data Analysis

## Overview
This project fetches and analyses flood monitoring data from the UK Environment Agency's API. Users can select a station, filter data for the last 24 hours, and visualise the measurements.

## API source
API Source
This project uses the UK Government's Flood Monitoring API:

- Base API URL: https://environment.data.gov.uk/flood-monitoring/id/stations

## Requirements

- Python 3.x
- pandas
- matplotlib
- PyQt5
- requests
- tabulate
- streamlit

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/KevinBeeson/CMCL_technical_test
    cd CMCL_technical_test
    ```

2. Create a virtual environment (recommended):
    ```bash
    python -m venv CMCL
    ```

3. Activate the virtual environment:
    - On Linux:
        ```bash
        source CMCL/bin/activate
        ```
    - On Windows:
        ```bash
        ./CMCL/scripts/activate
        ```

4. Install the required packages:

    ```bash
    pip install pandas tqdm matplotlib PyQt5 requests tabulate streamlit
    ```
    
    Or:
    
    ```bash
    pip install -r requirements.txt
    ```
## Features
- Fetches live flood monitoring station data
- Allows user selection of a station based on parameters like town or river name
- Supports filtering and visualisation of specific measurement types
- Plots the last 24 hours of data using Matplotlib

## Example run

To run the program, use the following command:
```bash
 streamlit run water_level.py 
```
The program will then fetch all the names of the stations, and the user can start narrowing down the database to their wanted water station or just select a water station.


The user can now narrow down these stations using the parameters ['id_name', 'town', 'catchmentName', 'riverName', 'label']; the program will narrow down this selection. Note the input won't be case sensitive.



This process repeats until only a single station is available or the user selects restart. If the user selects restart, all original stations will be available for them to choose from again.


You can select which numbers to plot. Multiple measurements can be plotted on one measurement. If there is only one station available, the program automatically plots that station.
