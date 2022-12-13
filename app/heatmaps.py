import plot
import config as cnf
import utils


def set_params_heatmaps(col1, col2):
    building_param = col1.radio('Select building', cnf.non_test_sites, key='hmaps_building')
    data_param = col1.radio('Select data', [key for key in cnf.data_param_dict.keys() if not key.startswith('_')], key='hmaps_data')
    time_param = col1.radio('Select average by', cnf.time_param_dict.keys(), key='hmaps_time')
    raw_data = col2.checkbox("Show raw data", value=False, key="hmaps_raw_data")
    return building_param, data_param, time_param, raw_data


def run_plots_heatmaps(df_dict, building_param, data_param, time_param, col):
    building_dict, param_dict, time_param_dict = utils.get_config_dicts(building_param, data_param, time_param)
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

