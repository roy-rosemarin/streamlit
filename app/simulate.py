# from sklearn.linear_model import LinearRegression


def sim_test_vent(df, shrink_usage_k):
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
        df2 = shrink_ac_usage(df2)

    df2 = shrink_ac_usage(df2)
    diff2outside = df2["Avg. room temperature (°C)"] - df2["Outside temperature (°C)"]
    pos_diff2outside = diff2outside.clip(lower=0, upper=None)
    neg_diff2outside = - diff2outside.clip(lower=None, upper=0)
    diff2ac = df2["Avg. room temperature (°C)"] - df2["Cooling temperature set point (°C)"]
    pos_diff2ac = diff2ac.clip(lower=0, upper=None)
    neg_diff2ac = - diff2ac.clip(lower=None, upper=0)
    ac_on = df2['Percentage of A/C usage (%)']
    ac_off = 1 - ac_on

    df2["Avg. room temperature (°C)"] = (ac_on * (df2["Avg. room temperature (°C)"]
                                                  - 0.3 * pos_diff2ac - 0.1 * pos_diff2outside)
                                         + ac_off * (0.95 * df2["Avg. room temperature (°C)"]
                                                     - 0.1 * pos_diff2outside))
    return df2


def shrink_ac_usage(df):
    prev_row = df.iloc[0, :]
    threshold = -1
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
