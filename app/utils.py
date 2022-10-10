import streamlit as st
import config as cnf


def line_space(cols_list, lines_list):
    for col, lines in zip(cols_list, lines_list):
        for i in range(lines):
            col.text("")


def convert_object_cols_to_boolean(df):
    df[df.columns[df.dtypes == 'object']] = (df[df.columns[df.dtypes == 'object']] == True)
    return df


@st.cache(allow_output_mutation=True, ttl=24*3600)
def get_config_dicts(buildnig_param, data_param, time_param):
    building_dict = cnf.sites_dict[buildnig_param]
    param_dict = cnf.data_param_dict[data_param]
    time_param_dict = cnf.time_param_dict[time_param]
    return building_dict, param_dict, time_param_dict
