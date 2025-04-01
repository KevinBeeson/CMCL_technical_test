import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import matplotlib
import copy
import streamlit as st
import numpy as np

matplotlib.use('Qt5Agg')
logging.getLogger().setLevel(logging.INFO)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def fetch_stations():
    try:
        st.write("Fetching stations...")
        response = requests.get("https://environment.data.gov.uk/flood-monitoring/id/stations")
        response.raise_for_status()
        data = response.json()['items']
        df = pd.DataFrame(data)
        for param in ['RLOIid', 'town', 'catchmentName', 'riverName', 'label']:
            df[param] = df[param].astype(str)
        return df
    except requests.RequestException as e:
        logging.error(f"Error fetching stations: {e}")
        st.error("Unable to retrieve station data.")
        return pd.DataFrame()


def fetch_station_readings(station_url):
    try:
        st.write("Fetching station readings...")
        response = requests.get(station_url + "/readings?_sorted")
        response.raise_for_status()
        readings = response.json()['items']
        df = pd.DataFrame(readings)
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        return df
    except requests.RequestException as e:
        logging.error(f"Error fetching station readings: {e}")
        st.error("Unable to retrieve station readings.")
        return pd.DataFrame()


def plot_data(df, types, unit_name, station_id):
    fig, ax = plt.subplots()
    for measurement_type in types:
        filtered = df[df['measure'] == measurement_type]
        label = measurement_type.split('/')[-1]
        ax.plot(filtered['dateTime'], filtered['value'], label=label)

    ax.legend()
    ax.set_xlabel('Time')
    ax.set_ylabel(f'Value / {unit_name}')
    ax.set_title(f'Last 24 hours of data at station {station_id}')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(0, 60, 15)))
    fig.autofmt_xdate()
    st.pyplot(fig)


if __name__ == '__main__':
    st.title("Water Level Monitoring")
    st.subheader("Select a station to monitor water levels")

    parameters = ['RLOIid', 'town', 'catchmentName', 'riverName', 'label']

    if 'data' not in st.session_state:
        st.session_state.data = fetch_stations()
        st.session_state.data_original = copy.deepcopy(st.session_state.data)

    if st.button("Reset"):
        st.session_state.data = copy.deepcopy(st.session_state.data_original)
        st.session_state.pop('data_station', None)

    filtered_data = st.session_state.data.copy()
    for param in parameters:
        options = [None] + sorted(filtered_data[param].dropna().unique().tolist())
        choice = st.selectbox(f"Select {param}", options)
        if choice:
            filtered_data = filtered_data[filtered_data[param] == choice].reset_index(drop=True)

    st.session_state.data = filtered_data
    st.write(filtered_data[parameters])

    if len(filtered_data) == 1:
        unit_name = filtered_data['measures'][0][0]['unitName']
        station_url = filtered_data['@id'][0]
        station_id = station_url.split('/')[-1]

        if 'data_station' not in st.session_state:
            st.session_state.data_station = fetch_station_readings(station_url)

        data_station = st.session_state.data_station
        types = data_station['measure'].unique()
        selected_types = st.multiselect("Select the type of measurement", types)

        if selected_types:
            now = pd.Timestamp.now().tz_localize('UTC')
            mask = (data_station['measure'].isin(selected_types)) & (data_station['dateTime'] >= now - pd.Timedelta(hours=24))
            filtered_readings = data_station[mask]
            st.write(filtered_readings)
            plot_data(filtered_readings, selected_types, unit_name, station_id)