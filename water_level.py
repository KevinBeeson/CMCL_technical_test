import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import matplotlib 
import copy
matplotlib.use('Qt5Agg')
logging.getLogger().setLevel(logging.INFO)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


if __name__ == '__main__':
    #get all the stations
    logging.info("Getting all the stations")
    response = requests.get("https://environment.data.gov.uk/flood-monitoring/id/stations")
    if response.status_code != 200:
        logging.error("Failed to get stations")
        exit(1)
    else:
        logging.info("Successfully got stations")
    

    #process the data into a pandas dataframe
    data=response.json()
    stations=data['items']
    data=pd.DataFrame(stations)
    id=[x.split('/')[-1] for x in data['@id']]
    data['id_name']=id

    #selects the station based on user input
    parameters=['id_name','town','catchmentName','riverName','label']
    data_original=copy.deepcopy(data)
    while len(data)>1:
        logging.info("Displaying the first 20 stations")
        logging.info("\n"+data[parameters][0:20].to_string())
        logging.info("There are "+str(len(data))+" stations")
        logging.info("Which station would you like to select? Enter parameter=parameter_value (e.g. town=Reading). If you would like to restart the selection, enter 'restart'")
        logging.info("The avaliable parameters are:"+str(parameters))
        selected_station=input()
        if any(x in selected_station for x in parameters) and '=' in selected_station:
            parameter,parameter_value=selected_station.split('=')
            #put the parameter value in title case
            mask=data[parameter]==parameter_value.title().strip()
            if sum(mask)==0:
                logging.info("No station with the specified parameter")
            else:
                data=data[mask]
                data.reset_index(drop=True,inplace=True)
        elif selected_station=='restart':
            data=copy.deepcopy(data_original)
        else:
            logging.info("Invalid input")
    
        


    unit_name=data['measures'][0][0]['unitName']
    example_station_id = data['@id'][0]
    logging.info("Getting the data for the station with id: "+example_station_id.split('/')[-1])
    response = requests.get(example_station_id+"/readings?_sorted")
    if response.status_code != 200:
        logging.error("Failed to get for the station")
        sys.exit(1)
    else:
        logging.info("Successfully got for the station")
    data_station=response.json()
    readings=data_station['items']
    data_station=pd.DataFrame(readings)

    #get the last measurement for the day 
    data_station['dateTime'] = pd.to_datetime(data_station['dateTime'])

    #get the types of measurements
    types=data_station['measure'].unique()
    if len(types)>1:
        logging.info("The types of measurements are: ")
        #print types with an index
        logging.info("Index Type")
        for i in range(len(types)):
            logging.info((i,types[i]))
        logging.info("Which type(s) of measurement would you like to plot? select the relevant index number, if multiples types separate by a comma (e.g. 0,1)")
        selected_types=input()
        selected_types=selected_types.split(',')
        for i in range(len(selected_types)):
            selected_types[i]=types[int(selected_types[i])]
        logging.info("Selected types of measurements are: ") 
        logging.info(selected_types)
    else:
        logging.info("The type of measurement is: "+types[0])
        selected_types=[types[0]]

    #create mask for the selected types
    mask = data_station['measure'].isin(selected_types)
    data_station = data_station[mask]

    #filter the data for the last 24 hours
    current_time = pd.Timestamp.now()
    current_time = current_time.tz_localize('UTC')
    # Use loc to filter for rows within the last 24 hours
    data_station_filtered = data_station.loc[data_station['dateTime'] >= (current_time - pd.Timedelta(hours=24))]

    # Alternatively, you can use mask:
    data_station_filtered = data_station_filtered.mask(data_station_filtered['dateTime'] < (current_time - pd.Timedelta(hours=24)))
    
    logging.info(data_station_filtered[['dateTime','value','measure']].to_string())
    #plot the data using matplotlib

    ax, fig = plt.subplots()
    for measurement_type in selected_types:
        data_station_filtered_type = data_station_filtered.loc[data_station_filtered['measure'] == measurement_type]
        type_name = measurement_type.split('/')[-1]
        plt.plot(data_station_filtered_type['dateTime'], data_station_filtered_type['value'], label=type_name)
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Value /'+unit_name)
    station_name=example_station_id.split('/')[-1]
    plt.title('Last 24 hours of data at station '+station_name)

    # Set major and minor ticks format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter(''))

    # Set major and minor ticks locator
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))

    # Align the minor ticks with the major ticks
    plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(byminute=range(0, 60, 15)))

    plt.gcf().autofmt_xdate()  # Rotation of x-axis labels for better readability

    plt.show()



