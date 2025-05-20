import pandas as pd
import numpy as np

def get_mean_value_df(df, column):
    avg_delay = df[column].tolist()
    try:
        avg_delay = [float(elt) for elt in avg_delay]
    except:
        return 0
    mean_delay = sum(avg_delay) / len(avg_delay)
    return mean_delay

def get_ratio_scheduled_cancelled(df):
    scheduled = get_mean_value_df(df, "Number of scheduled trains")
    cancelled = get_mean_value_df(df, "Number of cancelled trains")
    pct_cancelled = cancelled * 100 / scheduled
    return ((100 - pct_cancelled), pct_cancelled)

def get_ratio_national(df, station_name):
    len_national = len(df[(df["Departure station"] == station_name) & (df["Service"] == "National")])
    len_international = len(df[(df["Departure station"] == station_name) & (df["Service"] == "International")])
    if len_national == 0:
        return (0, 100)
    pct_national = len_international * 100 / len_national
    return ((100 - pct_national), pct_national)

def get_biggest_delay_cause(df):
    external_causes = get_mean_value_df(df, "Pct delay due to external causes")
    infrastructure_causes = get_mean_value_df(df, "Pct delay due to infrastructure")
    traffic_management_causes = get_mean_value_df(df, "Pct delay due to traffic management")
    rolling_stock_causes = get_mean_value_df(df, "Pct delay due to rolling stock")
    station_management_causes = get_mean_value_df(df, "Pct delay due to station management and equipment reuse")
    person_management_causes = get_mean_value_df(df, "Pct delay due to passenger handling (crowding, disabled persons, connections)")
    causes_names = ["External cause", "Infrastructure cause", "Traffic management cause", "Rollign stock cause", "Station management cause", "Person management cause"]
    causes = [external_causes, infrastructure_causes, traffic_management_causes, rolling_stock_causes, station_management_causes, person_management_causes]
    max_cause = max(causes)
    return (causes_names[causes.index(max_cause)], max_cause)

def get_values_per_station(df: pd.DataFrame, station_name):
    station_line = df.loc[df["Departure station"] == station_name]
    mean_delay = get_mean_value_df(station_line, "Average delay of all trains at departure")
    mean_duration = get_mean_value_df(station_line, "Average journey time")
    ratio_sch_canc = get_ratio_scheduled_cancelled(station_line)
    ratio_national = get_ratio_national(df, station_name)
    biggest_cause = get_biggest_delay_cause(station_line)
    dic_station = {
        "Average delay": mean_delay,
        "Average journey time": mean_duration,
        "Ratio scheduled/cancelled": ratio_sch_canc,
        "Ratio National/International": ratio_national,
        "Biggest delay cause": biggest_cause,
        }
    return dic_station
