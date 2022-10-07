app_version = 1.2
release_date = '05/10/2022'

figure_memory_scale = 0.2  # scaling the original seaborn in order to reduce memory usage

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
        'show_rooms': True,
        'field_substring': ['Room_Temp', 'RoomTemp'],
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    },
    'Percentage of A/C usage (%)': {
        'sites_dict_val': 'bms_collections',
        'show_rooms': True,
        'field_substring': ['State'],
        'fmt': '0.0%',
        'vmin': 0,
        'vmax': 1
    },
    'Avg. outside temperature (°C)': {
        'sites_dict_val': 'weather_collection',
        'show_rooms': False,
        'field_substring': ['temperature'],
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    }
}


aggregation_list = ("Date",
                    "Hour of Day")


sites_dict = {
    "Amro Malaga": {
        "bms_collections": ["BMS_Malaga_Climatizacion_Planta_S",
                    "BMS_Malaga_Climatizacion_Planta_B",
                    "BMS_Malaga_Climatizacion_Planta_1",
                    "BMS_Malaga_Climatizacion_Planta_2",
                    "BMS_Malaga_Climatizacion_Planta_3",
                    "BMS_Malaga_Climatizacion_Planta_4"],
        "floor_names": ["Planta S",
                        "Planta B",
                        "Planta 1",
                        "Planta 2",
                        "Planta 3",
                        "Planta 4"],
        'weather_collection': 'weather_Malaga',
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_malaga.csv",
        'gateway_reg_express': r'VRV([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (36.726308, -4.472825)
    },
    "Amro Seville": {
        "bms_collections": ["BMS_Seville_Climatizacion_Planta_S",
                    "BMS_Seville_Climatizacion_Planta_B",
                    "BMS_Seville_Climatizacion_Planta_1",
                    "BMS_Seville_Climatizacion_Planta_2",
                    "BMS_Seville_Climatizacion_Planta_3",
                    "BMS_Seville_Climatizacion_Planta_4",
                    "BMS_Seville_Climatizacion_Planta_5",
                    "BMS_Seville_Climatizacion_Planta_6",
                    "BMS_Seville_Climatizacion_Planta_7",
                    "BMS_Seville_Climatizacion_Planta_8",
                    "BMS_Seville_Climatizacion_Planta_9"],
        "floor_names": ["Planta S",
                        "Planta B",
                        "Planta 1",
                        "Planta 2",
                        "Planta 3",
                        "Planta 4",
                        "Planta_5",
                        "Planta 6",
                        "Planta 7",
                        "Planta 8",
                        "Planta 9"],
        'weather_collection': 'weather_Seville',
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_seville.csv",
        'gateway_reg_express': r'MIT([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (37.37821, -5.97253)
    }
}
