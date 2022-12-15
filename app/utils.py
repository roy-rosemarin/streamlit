import config as cnf
import streamlit as st


def format_row_wise(df, formatter):
    styler = df.style.highlight_null(props="color: transparent;")
    for row, row_formatter in formatter.items():
        if row not in styler.index:
            continue
        row_num = styler.index.get_loc(row)

        for col_num in range(len(styler.columns)):
            styler._display_funcs[(row_num, col_num)] = row_formatter
    return styler


def line_space(cols_list, lines_list):
    for col, lines in zip(cols_list, lines_list):
        for i in range(lines):
            col.text("")


def convert_object_cols_to_boolean(df):
    obj_cols = df[df.columns[df.dtypes == 'object']]
    obj_cols = (obj_cols is True) or (obj_cols == 'True')
    return df


@st.experimental_memo(show_spinner=False)
def get_config_dicts(building_param, data_param, time_param=None):
    building_dict = cnf.sites_dict[building_param]
    param_dict = cnf.data_param_dict[data_param]
    if time_param:
        time_param_dict = cnf.time_param_dict[time_param]
        return building_dict, param_dict, time_param_dict
    else:
        return building_dict, param_dict


@st.experimental_memo(show_spinner=False)
def info(duration, test_name, market_based_electricity_cost, location_based_co2):
    title = 'See how it is calculated'
    intro = [f'''
        Pre-experiment calibration results is a summary statistics table comparing the test and control groups over 
        different metrics over a {duration.days}-day period to ensure that the groups are similar and any 
        differences in the results can be attributed to the experiment.''',
             f'''
        'A/B testing period results is a summary statistics table comparing the test and control groups over 
        different metrics over the test {duration.days}-day period to measure the 
        differences in the groups that can be attributed to the experiment.''',
             f'''
        Pre/Post A/B testing results is a summary statistics table comparing the trends between the 
        Pre-experiment calibration period and the A/B testing period 
        to measure relative changes in the groups that can be attributed to the experiment.''']
    body = f'''
        Number of rooms - number of rooms that belong to each group. The rest of the metrics below provide 
        **{'per-room'}** averages for the rooms that belong to each group over the full period.\n
        Cooling temperature set point (°C) - avg. AC cooling set point.\n
        Percentage of A/C usage (%) - average percentage of time that AC is being used.\n
        Average room electricity consumption (kWh) - approximate average electricity consumption.\n
        This is calculated as follows:
        * VRV internal units - Total consumption in KW of floors 1-8 from BMS over 13 days between dates 21.10.2022-02.11.2022.
        * VRV external units - Total consumption in KW of external VRV units from BMS over 13 days between dates 21.10.2022-02.11.2022
        * average % AC usage - 40% over 13 days between dates 21.10.2022-02.11.2022
        * Number of active rooms - 280 occupied rooms (out of a total of 339 rooms in Seville). 
        multiplied by 85.6%, which is the relative power capacity of the climatization external units for the rooms and clusters.
        Then the formula is: \n
        Avg. tenants VRV kW consumption = (VRV internal units + VRV external units) / (#Hours) = 29.88 kW\n
        Avg. tenants VRV kWh consumption per occupied room per day  = Avg. tenants VRV kWh consumption * 24 / Number of active rooms = 2.58\n
        Average room electricity consumption (kWh) = Avg. tenants VRV kWh consumption per occupied room per day * duration in days * 
        Percentage of A/C usage (%) / average % AC usage = 2.58 * duration in days * Percentage of A/C usage (%) / 40%
        \n
        Average room electricity cost (€) (ex. VAT) - approximate average electricity cost calculated by 
        multiplying electricity consumption (kWh) by the market-based cost factor of
        {market_based_electricity_cost} €/kWh for test "{test_name}".\n
        Average room carbon footprint (kg CO2) - approximate average carbon footprint (kg CO2) calculated by 
        multiplying electricity consumption (kWh) by the location-based emission factor of
        {location_based_co2} kgCO2/kWh for test "{test_name}"
        '''
    return title, intro, body
