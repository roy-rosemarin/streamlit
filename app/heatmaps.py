import plot
import config as cnf
import utils


def set_params_heatmaps(col):
    building_param = col.radio('Select building', cnf.sites_dict.keys(), key='heatmaps')
    data_param = col.radio('Select data', cnf.data_param_dict.keys())
    time_param = col.radio('Select average by', cnf.time_param_dict.keys())
    return building_param, data_param, time_param


def run_flow_heatmaps(db, collect_name, collect_title, building_param, data_param, time_param, col):
    building_dict, param_dict, time_param_dict = utils.get_config_dicts(building_param, data_param, time_param)
    df_dict = utils.get_cooked_df(db, collect_name, collect_title, building_dict, param_dict, time_param_dict)
    for i, (title, df) in enumerate(df_dict.items()):
        plot.plot_heatmap(
            df=df,
            time_param=time_param,
            plot_parms=(param_dict['fmt'], param_dict['vmin'], param_dict['vmax']),
            title=title,
            # xlabel=time_param,
            # ylabel=f'{collect_title}\nrooms' + '\n',
            to_zone=building_dict['time_zone'],
            scale=cnf.figure_memory_scale,
            col=col)

