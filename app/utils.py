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
