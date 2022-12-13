from datetime import datetime, timedelta
import times
import numpy as np


app_version = 1.5
release_date = '21/10/2022'
test = True

figure_memory_scale = 0.25  # scaling the original seaborn in order to reduce memory usage
cert_file = "amro-partners-firebase-adminsdk-syddx-7de4edb3c4.json"  # certification file for firebase authentication
storage_bucket = 'amro-partners.appspot.com'

tabs = ["HEATMAPS", "CHARTS", "EXPERIMENTS"]


'''
data_param_dict maps keys strings to be selected by user (as keys) to a list of parameters:
sites_dict_val: value to look in sites_dict[site] for the collection(s) name
field_keyword:substrings of the required field within the firebase collection
fmt: heatmap text format
vmin: heatmap scale minimum
vmax: heatmap scale maximum
'''
data_param_dict = {
    "Avg. room temperature (°C)": {
        'sites_dict_val': 'VRV_collections',
        'is_rooms': True,
        'field_keyword': ['Room_Temp', 'RoomTemp'],
        'match_keyword': 'substring',  # 'substring' or 'exact' match for field_keyword
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    },
    "Cooling temperature set point (°C)": {
        'sites_dict_val': 'VRV_setpoint_collections',
        'is_rooms': True,
        'field_keyword': ['SetTempCool'],
        'match_keyword': 'substring',  # 'substring' or 'exact' match for field_keyword
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    },
    # "Heating temperature set point (°C)": {
    #     'sites_dict_val': 'VRV_setpoint_collections',
    #     'is_rooms': True,
    #     'field_keyword': ['SetTempHeat'],
    #     'match_keyword': 'substring',  # 'substring' or 'exact' match for field_keyword
    #     'fmt': '.1f',
    #     'vmin': 15,
    #     'vmax': 40
    # },
    'Percentage of A/C usage (%)': {
        'sites_dict_val': 'VRV_collections',
        'is_rooms': True,
        'field_keyword': ['OnOffState', 'State_BI'],
        'match_keyword': 'substring',  # 'substring' or 'exact' match for field_keyword
        'fmt': '0.0%',
        'vmin': 0,
        'vmax': 1
    },
    'Outside temperature (°C)': {
        'sites_dict_val': 'weather_collection',
        'is_rooms': False,
        'field_keyword': ['temperature'],
        'match_keyword': 'exact',  # 'substring' or 'exact' match for field_keyword
        'fmt': '.1f',
        'vmin': 15,
        'vmax': 40
    },
    '_Outside temperature 3h prediction (°C)': {
        'sites_dict_val': 'weather_collection',
        'is_rooms': False,
        'field_keyword': ['3h_temperature_interp'],
        'match_keyword': 'exact',  # 'substring' or 'exact' match for field_keyword
    },
}


# TODO: we need to localise the start_date and end_date
time_param_dict = {
    "Date (last 7 days)": {
        'start_date_utc': (times.utc_now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0),
        'end_date_utc': (times.utc_now()).replace(hour=0, minute=0, second=0, microsecond=0),
        'aggregation_field_name': 'Date',
        'aggregation_strftime': '%Y-%m-%d\n%A'
    },
    "Hour of Day (last 7 days)": {
        'start_date_utc': (times.utc_now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0),
        'end_date_utc': (times.utc_now()).replace(hour=0, minute=0, second=0, microsecond=0),
        'aggregation_field_name': 'Hour',
        'aggregation_strftime': '%H'
    },
    # "Latest reading": {
    #     'start_date_utc': (times.utc_now() - timedelta(minutes=15)),
    #     'end_date_utc': (times.utc_now()),
    #     'aggregation_field_name': 'Local time',
    #     'aggregation_strftime': '%Y-%m-%d %H:%M:%S'
    # },
}


sites_dict = {
    "Amro Seville fan speed pilot CL01": {
        "VRV_collections": [('BMS_Seville_Climatizacion_VRV', None)],
        'VRV_setpoint_collections': [('BMS_Seville_Climatizacion_VRV_setpoints', None)],
        'weather_collection': [('weather_Seville', 'Outside temperature (°C) Seville')],
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_seville_CL01_exp.csv",
        'gateway_reg_express': r'MIT([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (37.37821, -5.97253),
        'floors_order': ['Control',
                         'Test'],
        'floors_col': 'Group',
        'start_exp_date_utc': datetime(2022, 12, 2, 12, 0),
        'end_exp_date_utc': datetime(2022, 12, 30, 12, 0),
            'calibration_days': 7
    },
    "Amro Seville ventilation temp pilot CL02": {
        "VRV_collections": [('BMS_Seville_Climatizacion_VRV', None)],
        'VRV_setpoint_collections': [('BMS_Seville_Climatizacion_VRV_setpoints', None)],
        'weather_collection': [('weather_Seville', 'Outside temperature (°C) Seville')],
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_seville_CL02_exp.csv",
        'gateway_reg_express': r'MIT([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (37.37821, -5.97253),
        'floors_order': ['Control',
                         'Test'],
        'floors_col': 'Group',
        'start_exp_date_utc': datetime(2022, 12, 2, 12, 0),
        'end_exp_date_utc': datetime(2022, 12, 30, 12, 0),
        'calibration_days': 7
    },
    "Amro Seville": {
        "VRV_collections": [('BMS_Seville_Climatizacion_VRV', None)],
        'VRV_setpoint_collections': [('BMS_Seville_Climatizacion_VRV_setpoints', None)],
        'weather_collection': [('weather_Seville', 'Outside temperature (°C) Seville')],
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_seville.csv",
        'gateway_reg_express': r'MIT([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (37.37821, -5.97253),
        'floors_order': ["Planta S", "Planta B", "Planta 1", "Planta 2", "Planta 3", "Planta 4",
                         "Planta 5", "Planta 6", "Planta 7", "Planta 8", "Planta 9"],
        'floors_col': 'Title'
    },
    "Amro Malaga": {
        "VRV_collections": [("BMS_Malaga_Climatizacion_Planta_S", "Planta S"),
                            ("BMS_Malaga_Climatizacion_Planta_B", "Planta B"),
                            ("BMS_Malaga_Climatizacion_Planta_1", "Planta 1"),
                            ("BMS_Malaga_Climatizacion_Planta_2", "Planta 2"),
                            ("BMS_Malaga_Climatizacion_Planta_3",  "Planta 3"),
                            ("BMS_Malaga_Climatizacion_Planta_4", "Planta 4")],
        'VRV_setpoint_collections': [],
        'weather_collection': [('weather_Malaga', 'Outside temperature (°C) Malaga')],
        'time_zone': 'Europe/Madrid',
        'rooms_file': "rooms_codes_malaga.csv",
        'gateway_reg_express': r'VRV([\d]+).[\w.-]+_([\d]+).',
        'coordinates': (36.726308, -4.472825),
        'floors_order': ["Planta S", "Planta B", "Planta 1", "Planta 2", "Planta 3",  "Planta 4"],
        'floors_col': 'Title'
    },
}

test_build_terms = ['pilot', 'exp', 'flight']
test_sites = [s for s in sites_dict.keys() if any([sub in s for sub in test_build_terms])]
non_test_sites = [s for s in sites_dict.keys() if all([sub not in s for sub in test_build_terms])]


# Experiment settings
avg_group_df_name = 'summary avg'  # avg across the group per timestamp
avg_pre_df_name = 'summary avg pre'  # avg across the group
avg_post_df_name = 'summary avg post'  # avg across the group

num_rooms_name = 'Number of rooms'  # number of rooms across the group

room_temp_name = "Avg. room temperature (°C)"  # avg. room temperature
temp_setpoint_name = 'Cooling temperature set point (°C)'
ac_usage_name = 'Percentage of A/C usage (%)'
elect_consump_name = 'Average room electricity consumption (kWh)'  # number of rooms across the group
elect_cost_name = 'Average room electricity cost (€) (ex. VAT)'  # number of rooms across the group
elect_carbon_name = 'Average room carbon footprint (kg CO2)'  # number of rooms across the group


formatters = {
    num_rooms_name: lambda x: f"{round(x)}" if x == x else x,
    room_temp_name: lambda x: f"{x:.2f}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.2f}, {x[1]:.2f}]",
    temp_setpoint_name: lambda x: f"{x:.2f}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.2f}, {x[1]:.2f}]",
    ac_usage_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
    elect_consump_name: lambda x: f"{x:.2f}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.2f}, {x[1]:.2f}]",
    elect_cost_name: lambda x: f"{x:.2f}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.2f}, {x[1]:.2f}]",
    elect_carbon_name: lambda x: f"{x:.2f}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.2f}, {x[1]:.2f}]"
}

formatters2 = {
    num_rooms_name: lambda x: f"{round(x)}" if x == x else x,
    room_temp_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
    temp_setpoint_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
    ac_usage_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
    elect_consump_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
    elect_cost_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
    elect_carbon_name: lambda x: f"{x:.1%}" if type(x) in (float, np.float32, np.float64) else f"[{x[0]:.1%}, {x[1]:.1%}]",
}

metrics = [room_temp_name,
           temp_setpoint_name,
           ac_usage_name,
           elect_consump_name,
           elect_cost_name,
           elect_carbon_name]

test_group = "Test"
control_group = "Control"

time_agg_dict = {
    'Daily': '1D',
    'Hourly': '1H',
    '15 minutes': '15T'
}
