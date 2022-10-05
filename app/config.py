app_version = 1.2
release_date = '05/10/2022'

figure_memory_scale = 0.2  # scaling the original seaborn in order to reduce memory usage

cert_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.json"  # certification file for firebase authentication

temp_data_list = ("",
                    "Avg. degrees (°C)",
                    'Percentage of usage (%)')


aggregation_list = ("",
                    "Date",
                    "Hour of Day")


sites_dict = {
    "Amro Malaga": {
        "collections": ["BMS_Malaga_Climatizacion_Planta_S",
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
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_malaga.csv",
        'gateway_reg_express': r'VRV([\d]+).[\w.-]+_([\d]+).'
    },
    "Amro Seville": {
        "collections": ["BMS_Seville_Climatizacion_Planta_S",
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
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_seville.csv",
        'gateway_reg_express': r'MIT([\d]+).[\w.-]+_([\d]+).'
    }
}