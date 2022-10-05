import streamlit as st


def line_space(cols_list, lines_list):
    for col, lines in zip(cols_list, lines_list):
        for i in range(lines):
            col.text("")


def set_columns():
    col1, col2, col3 = st.columns([2, 3, 2])


def convert_object_cols_to_boolean(df):
    df[df.columns[df.dtypes == 'object']] = (df[df.columns[df.dtypes == 'object']] == True)
    return df