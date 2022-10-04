figure_memory_scale = 0.2 # scaling the original seaborn in order to reduce memory usage

to_zone = 'Europe/Madrid'  # local zone
cert_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.json"  # certification file for firebase authentication

room_dict_sites = {
    "Amro Malaga": "rooms_codes_malaga.csv",
    "Amro Seville": "rooms_codes_seville.csv"
}

gateway_room_dict_sites = {
    "Amro Malaga": r'VRV([\d]+).[\w.-]+_([\d]+).',
    "Amro Seville": r'MIT([\d]+).[\w.-]+_([\d]+).'
}

building_list = ("",
              "Amro Malaga",
              "Amro Seville")

temp_data_list = ("",
                    "Avg. degrees (°C)",
                    '"On" frequency (%)')

collect_list_general = ["",
                        "All"]

collect_dict_buildings = {
    "Amro Malaga": ["BMS_Malaga_Climatizacion_Planta_S",
                "BMS_Malaga_Climatizacion_Planta_B",
                "BMS_Malaga_Climatizacion_Planta_1",
                "BMS_Malaga_Climatizacion_Planta_2",
                "BMS_Malaga_Climatizacion_Planta_3",
                "BMS_Malaga_Climatizacion_Planta_4"],
    "Amro Seville": ["BMS_Seville_Climatizacion_Planta_S",
                "BMS_Seville_Climatizacion_Planta_B",
                "BMS_Seville_Climatizacion_Planta_1",
                "BMS_Seville_Climatizacion_Planta_2",
                "BMS_Seville_Climatizacion_Planta_3",
                "BMS_Seville_Climatizacion_Planta_4",
                "BMS_Seville_Climatizacion_Planta_5",
                "BMS_Seville_Climatizacion_Planta_6",
                "BMS_Seville_Climatizacion_Planta_7",
                "BMS_Seville_Climatizacion_Planta_8",
                "BMS_Seville_Climatizacion_Planta_9"]
}

aggregation_list = ("",
                    "Date",
                    "Hour of Day")


