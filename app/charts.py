import config as cnf
import rooms


def set_params(col):
    building_param = col.radio('Select building', cnf.sites_dict.keys(), key='chart')
    building_dict = cnf.sites_dict[building_param]
    floor_param = col.radio('Select floor', building_dict['floors_order'])
    floor_to_rooms_dict = rooms.get_floor_to_rooms_dict(building_dict['rooms_file'])
    room_param = col.selectbox('Select room', floor_to_rooms_dict[floor_param])
    return building_param, floor_param, room_param


def run_flow_charts(col):
    col.write('PLACEHOLDER')
    return 1
