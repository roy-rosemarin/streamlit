import firebase_database as fbdb
import rooms
import plot
import config as cnf
import utils
# import required for hashing while caching data for streamlit
# import google.cloud.firestore_v1.client as gcc


def set_params(col):
    building_param = col.radio('Select building', cnf.sites_dict.keys(), key='heatmaps')
    data_param = col.radio('Select data', cnf.data_param_dict.keys())
    time_param = col.radio('Select average by', cnf.time_param_dict.keys())
    return building_param, data_param, time_param


# @st.cache(allow_output_mutation=True, ttl=4*3600,
#           hash_funcs={dict: lambda _: None, gcc.Client: lambda _: None})
def run_flow_heatmaps(db, collect_name, collect_title, building_param, data_param, time_param, col):
    building_dict, param_dict, time_param_dict = utils.get_config_dicts(building_param, data_param, time_param)
    df_pd = fbdb.get_firebase_data(db, collect_name, time_param_dict['start_date_utc'], time_param_dict['end_date_utc'],
                                   param_dict['field_substring'])
    fmt, vmin, vmax = param_dict['fmt'], param_dict['vmin'], param_dict['vmax']
    if param_dict['is_rooms']:
        rooms_dict = rooms.get_code_to_room_dict(building_dict['rooms_file'])
        gateway_room_pattern = building_dict['gateway_reg_express']
        df_pd = rooms.map_rooms_names(df_pd.copy(), rooms_dict, gateway_room_pattern)
        floors_order_dict = {k: v for v, k in enumerate(building_dict['floors_order'])}
        for rooms_title in sorted(set(df_pd.columns.get_level_values(0)),
                                  key=lambda item: floors_order_dict.get(item, len(floors_order_dict))):
            condition = df_pd.columns.get_level_values(0) == rooms_title
            dff = df_pd.loc[:, condition]
            dff.columns = dff.columns.get_level_values(1)
            plot.plot_heatmap(
                df=dff,
                time_param=time_param,
                plot_parms=(fmt, vmin, vmax),
                title=collect_title if collect_title else rooms_title,
                # xlabel=time_param,
                # ylabel=f'{collect_title}\nrooms' + '\n',
                to_zone=building_dict['time_zone'],
                scale=cnf.figure_memory_scale,
                col=col)
    else:
        plot.plot_heatmap(
            df=df_pd,
            time_param=time_param,
            plot_parms=(fmt, vmin, vmax),
            title=collect_title,
            #xlabel=time_param,
            #ylabel=f'{collect_title}\nrooms' + '\n',
            to_zone=building_dict['time_zone'],
            scale=cnf.figure_memory_scale,
            col=col)
