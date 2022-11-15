# from sklearn.linear_model import LinearRegression
import numpy as np


def sim_test_vent(df, shrink_usage_k, building_dict):
    '''
    # Code for regression based simulation
    X = df.iloc[:, :0]
    y = df.iloc[:, :0]

    y['temp_diff'] = df["Avg. room temperature (°C)"].shift(-1).diff()
    X["diff2outside"] = df["Avg. room temperature (°C)"] - df["Outside temperature (°C)"]
    X["pos_diff2outside"] = X["diff2outside"].clip(lower=0, upper=None)
    X["neg_diff2outside"] = - X["diff2outside"].clip(lower=None, upper=0)
    X["diff2ac"] = df['Percentage of A/C usage (%)'] * (df["Avg. room temperature (°C)"]
                                                          - df["Cooling temperature set point (°C)"])
    X["pos_diff2ac"] = X["diff2ac"].clip(lower=0, upper=None)
    X["neg_diff2ac"] = - neg_diff2outside.clip(lower=None, upper=0)

    reg = LinearRegression().fit(X, y)
    print(reg.coef_)
    print(reg.predict(X))  # make predictions
    '''
    df2 = df.copy()
    for i in range(shrink_usage_k):
        df2 = shrink_ac_usage(df2, building_dict['shrink_ac_threshold'])

    diff2outside = df2["Avg. room temperature (°C)"] - df2["Outside temperature (°C)"]
    pos_diff2outside = diff2outside.clip(lower=0, upper=None)
    neg_diff2outside = - diff2outside.clip(lower=None, upper=0)
    diff2ac = df2["Avg. room temperature (°C)"] - df2["Cooling temperature set point (°C)"]
    pos_diff2ac = diff2ac.clip(lower=0, upper=None)
    neg_diff2ac = - diff2ac.clip(lower=None, upper=0)
    ac_on = df2['Percentage of A/C usage (%)']
    ac_off = 1 - ac_on

    gradual_mult = np.ones(len(df2))
    if building_dict['is_gradual']:
        gradual_mult[:100] = np.arange(100) / 100

    building_dict['is_gradual'] * np.arange(len(df2)) / len(df2) + (1 - building_dict['is_gradual'])
    diff = (ac_on * (0.25 * pos_diff2ac + building_dict['pos_diff2outside_coef'] * pos_diff2outside)
            + ac_off * (0.035 * df2["Avg. room temperature (°C)"] + building_dict['pos_diff2outside_coef'] * pos_diff2outside))

    df2["Avg. room temperature (°C)"] = (df2["Avg. room temperature (°C)"] - gradual_mult * diff)

    return df2


def shrink_ac_usage(df, shrink_ac_threshold):
    prev_row = df.iloc[0, :]
    threshold = -shrink_ac_threshold
    for index, row in df.iterrows():
        if ((row['Percentage of A/C usage (%)'] and not prev_row['Percentage of A/C usage (%)']) and
                (row["Avg. room temperature (°C)"] - prev_row["Avg. room temperature (°C)"] >= threshold)):
            df.at[index, 'Percentage of A/C usage (%)'] = False
        prev_row = row

    prev_row = df.iloc[-1, :]
    for index, row in df[::-1].iterrows():
        if ((row['Percentage of A/C usage (%)'] and not prev_row['Percentage of A/C usage (%)']) and
                (row["Avg. room temperature (°C)"] - prev_row["Avg. room temperature (°C)"] >= threshold)):
            df.at[index, 'Percentage of A/C usage (%)'] = False
        prev_row = row
    return df
