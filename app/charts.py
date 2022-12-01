import rooms
import config as cnf
import streamlit as st
import plot


def set_params_charts(col):
    building_param = col.radio('Select building', cnf.non_test_sites, key='chart_building')
    building_dict = cnf.sites_dict[building_param]
    floor_param = col.radio('Select floor', building_dict['floors_order'], key='chart_floor')
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    room_param = col.selectbox('Select room', sorted(floor_to_rooms_dict[floor_param]), key='chart_room')
    return building_param, floor_param, room_param


def run_flow_charts(df, col):  #(db, building_param, floor_param, room_param, col):
    max_datetime = df.index[-1]
    if st.session_state.show_raw_data_charts:
        col.dataframe(df, use_container_width=True)
    else:
        col.altair_chart(plot.charts(df, max_datetime).interactive(), use_container_width=True)
