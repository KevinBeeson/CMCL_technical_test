# Import necessary libraries
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import matplotlib 
import copy
import streamlit as st
import numpy as np

# Set matplotlib backend
matplotlib.use('Qt5Agg')

# Set logging level to INFO
logging.getLogger().setLevel(logging.INFO)

# Set pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# Main Streamlit app starts here
if __name__ == '__main__':
    # Define parameters for filtering station data
    parameters = ['RLOIid', 'town', 'catchmentName', 'riverName', 'label']

    # Check if data already in session; if not, fetch station data from API
    if 'data' not in st.session_state:
        logging.info("Getting all the stations")
        st.write("Getting all the stations")

        response = requests.get("https://environment.data.gov.uk/flood-monitoring/id/stations")
        if response.status_code != 200:
            logging.error("Failed to get stations")
            st.write("Failed to get stations")
            exit(1)
        else:
            logging.info("Successfully got stations")
            st.write("Successfully got stations")

        # Convert API response to DataFrame
        stations = response.json()['items']
        data = pd.DataFrame(stations)

        # Ensure specific columns are strings
        for x in parameters:
            data[x] = data[x].astype(str)

        # Cache data in Streamlit session
        st.session_state.data = data
        st.session_state.data_original = copy.deepcopy(data)
    else:
        logging.info("Using cached data")
        st.write("Using cached data")
        data = st.session_state.data

    # Streamlit UI: title and subheader
    st.title("Water Level Monitoring")
    st.subheader("Select a station to monitor water levels")

    # Add reset button to clear filters
    if st.button("Reset"):
        logging.info("Resetting the selection")
        st.session_state.data = copy.deepcopy(st.session_state.data_original)
        if 'data_station' in st.session_state:
            del st.session_state['data_station']

    # Create dropdown filters for each parameter
    filtered_data = st.session_state.data.copy()
    make_choice = {}   
    for value, name in enumerate(parameters):
        options = [None] + sorted(filtered_data[name].explode().dropna().unique().tolist())
        choice = st.selectbox(f"Select {name}", options)
        make_choice[name] = choice

        if choice is not None:
            filtered_data = filtered_data[filtered_data[name] == choice]
            filtered_data.reset_index(drop=True, inplace=True)

    # Show the filtered data
    st.session_state.data = filtered_data
    st.write(filtered_data[parameters])

    # If only one station is selected, fetch and display its readings
    if len(filtered_data) == 1:
        logging.info("Displaying the selected station")

        unit_name = filtered_data['measures'][0][0]['unitName']
        example_station_id = filtered_data['@id'][0]
        logging.info("Getting the data for station: " + example_station_id.split('/')[-1])

        # Fetch station reading data if not already cached
        if 'data_station' not in st.session_state:
            logging.info("Getting the data for the station")
            st.write("Getting the data for the station")
            response = requests.get(example_station_id + "/readings?_sorted")
            if response.status_code != 200:
                logging.error("Failed to get data for the station")
                sys.exit(1)

            data_station = response.json()['items']
            data_station = pd.DataFrame(data_station)
            data_station['dateTime'] = pd.to_datetime(data_station['dateTime'])
            st.session_state.data_station = data_station
        else:
            logging.info("Using cached data for the station")
            st.write("Using cached data for the station")
            data_station = st.session_state.data_station

        # Show measurement types and allow user to select
        types = data_station['measure'].unique()
        selected_types = st.multiselect("Select the type of measurement", types)

        if selected_types:
            logging.info(f"Filtering data by measure = {selected_types}")

            # Filter by selected measure types
            mask = data_station['measure'].isin(selected_types)
            data_station = data_station[mask]

            # Filter data for the last 24 hours
            current_time = pd.Timestamp.now().tz_localize('UTC')
            data_station_filtered = data_station.loc[data_station['dateTime'] >= (current_time - pd.Timedelta(hours=24))]

            st.write(data_station_filtered)

            # Plot the filtered data
            ax, fig = plt.subplots()
            for measurement_type in selected_types:
                type_data = data_station_filtered[data_station_filtered['measure'] == measurement_type]
                type_name = measurement_type.split('/')[-1]
                plt.plot(type_data['dateTime'], type_data['value'], label=type_name)

            plt.legend()
            plt.xlabel('Time')
            plt.ylabel('Value / ' + unit_name)
            station_name = example_station_id.split('/')[-1]
            plt.title(f'Last 24 hours of data at station {station_name}')

            # Configure the x-axis date formatting
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter(''))
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
            plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(0, 60, 15)))
            plt.gcf().autofmt_xdate()

            # Render the plot in Streamlit
            st.pyplot(ax)
