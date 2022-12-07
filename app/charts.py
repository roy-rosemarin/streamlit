import rooms
import config as cnf
import streamlit as st
import plot


def set_params_charts(col1, col2):
    building_param = col1.radio('Select building', cnf.non_test_sites, key='chart_building')
    building_dict = cnf.sites_dict[building_param]
    floor_param = col1.radio('Select floor', building_dict['floors_order'], key='chart_floor')
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'], building_dict['floors_col'])
    room_param = col1.selectbox('Select room', sorted(floor_to_rooms_dict[floor_param]), key='chart_room')
    raw_data = col2.checkbox("Show raw data", value=False, key="chart_raw_data")
    return building_param, floor_param, room_param, raw_data


def run_flow_charts(df, _col):  #(db, building_param, floor_param, room_param, col):
    max_datetime = df.index[-1]
    if st.session_state.chart_raw_data:
        _col.dataframe(df, use_container_width=True)
    else:
        _col.altair_chart(plot.charts(df, max_datetime).interactive(), use_container_width=True)
