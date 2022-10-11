from datetime import datetime, timedelta


app_version = 1.3
release_date = '10/10/2022'

figure_memory_scale = 0.25  # scaling the original seaborn in order to reduce memory usage

cert_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.json"  # certification file for firebase authentication

'''
data_param_dict maps keys strings to be selected by user (as keys) to a list of parameters:
sites_dict_val: value to look in sites_dict[site] for the collection(s) name
field_substring:substrings of the required field within the firebase collection
fmt: heatmap text format
vmin: heatmap scale minimum
vmax: heatmap scale maximum
'''
data_param_dict = {
    "Avg. room temperature (°C)": {
        'sites_dict_val': 'bms_collections',
        'is_rooms': True,
        'field_substring': ['Room_Temp', 'RoomTemp'],
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    },
    'Percentage of A/C usage (%)': {
        'sites_dict_val': 'bms_collections',
        'is_rooms': True,
        'field_substring': ['State'],
        'fmt': '0.0%',
        'vmin': 0,
        'vmax': 1
    },
    'Outside temperature (°C)': {
        'sites_dict_val': 'weather_collection',
        'is_rooms': False,
        'field_substring': ['temperature'],
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    }
}

time_param_dict = {
    "Date (last 7 days)": {
        'start_date_utc': (datetime.utcnow() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0),
        'end_date_utc': (datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0),
        'aggregation_field_name': 'Date',
        'aggregation_strftime': '%Y-%m-%d'
    },
    "Hour of Day (last 7 days)": {
        'start_date_utc': (datetime.utcnow() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0),
        'end_date_utc': (datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0),
        'aggregation_field_name': 'Hour',
        'aggregation_strftime': '%H'
    },
    "Now (last 15 minutes)": {
        'start_date_utc': (datetime.utcnow() - timedelta(minutes=15)),
        'end_date_utc': (datetime.utcnow()),
        'aggregation_field_name': 'Local time',
        'aggregation_strftime': '%Y-%m-%d %H:%M:%S'
    },
}


sites_dict = {
    "Amro Malaga": {
        "bms_collections": [("BMS_Malaga_Climatizacion_Planta_S", "Planta S"),
                            ("BMS_Malaga_Climatizacion_Planta_B", "Planta B"),
                            ("BMS_Malaga_Climatizacion_Planta_1", "Planta 1"),
                            ("BMS_Malaga_Climatizacion_Planta_2", "Planta 2"),
                            ("BMS_Malaga_Climatizacion_Planta_3",  "Planta 3"),
                            ("BMS_Malaga_Climatizacion_Planta_4", "Planta 4")],
        'weather_collection': [('weather_Malaga', 'Outside temperature (°C) Malaga')],
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_malaga.csv",
        'gateway_reg_express': r'VRV([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (36.726308, -4.472825)
    },
    "Amro Seville": {
        "bms_collections": [("BMS_Seville_Climatizacion_Planta_S", "Planta S"),
                            ("BMS_Seville_Climatizacion_Planta_B", "Planta B"),
                            ("BMS_Seville_Climatizacion_Planta_1", "Planta 1"),
                            ("BMS_Seville_Climatizacion_Planta_2", "Planta 2"),
                            ("BMS_Seville_Climatizacion_Planta_3", "Planta 3"),
                            ("BMS_Seville_Climatizacion_Planta_4", "Planta 4"),
                            ("BMS_Seville_Climatizacion_Planta_5", "Planta 5"),
                            ("BMS_Seville_Climatizacion_Planta_6", "Planta 6"),
                            ("BMS_Seville_Climatizacion_Planta_7", "Planta 7"),
                            ("BMS_Seville_Climatizacion_Planta_8", "Planta 8"),
                            ("BMS_Seville_Climatizacion_Planta_9", "Planta 9")],
        'weather_collection': [('weather_Seville', 'Outside temperature (°C) Seville')],
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_seville.csv",
        'gateway_reg_express': r'MIT([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (37.37821, -5.97253)
    }
}
