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

def get_sum_value_df(df, column):
    avg_delay = df[column].tolist()
    try:
        avg_delay = [float(elt) for elt in avg_delay]
    except:
        return 0
    mean_delay = sum(avg_delay)
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
    causes_names = ["external issues", "infrastructure issues", "traffic management issues", "rollign stock issues", "station management issues", "person management issues"]
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

def get_mean_times_for_route(df: pd.DataFrame, start: str, end: str):
    # On filtre dans les deux sens
    route_df = df.loc[
        ((df['Departure station'] == start) & (df['Arrival station'] == end)) |
        ((df['Departure station'] == end) & (df['Arrival station'] == start))
    ]

    # On calcule les moyennes
    mean_journey_time = route_df["Average journey time"].mean()
    mean_delay_time = route_df["Average delay time"].mean()
    ratio_schedule = route_df["Number of scheduled trains"].mean()
    ratio_cancel = route_df["Number cancelled trains"].mean()

    return {
        "Average journey time": mean_journey_time,
        "Average delay time": mean_delay_time,
        "Ratio": ratio_cancel * 100 / ratio_schedule
    }


def get_route_info(start, end, df: pd.DataFrame):
    # Inverser si les données sont dans l'autre sens
    if not df.loc[(df['Departure station'] == end) & (df['Arrival station'] == start)].empty:
        start, end = end, start  # switch baby

    # Filtrage dans les deux sens
    station_lines = df.loc[
        ((df['Departure station'] == start) & (df['Arrival station'] == end)) |
        ((df['Departure station'] == end) & (df['Arrival station'] == start))
    ]

    # Si c'est vide, on retourne 1
    if station_lines.empty:
        return 1

    # Calcul des moyennes
    mean_journey_time = get_mean_value_df(station_lines, "Average journey time" )
    mean_delay = get_mean_value_df(station_lines, "Average delay of all trains at departure")

    dic = {
        "Average journey time": round(mean_journey_time, 2),
        "Average delay": round(mean_delay, 2),
    }

    return dic

def get_all_infos(df: pd.DataFrame):
    mean_journey_time = get_mean_value_df(df, "Average journey time" )
    mean_delay = get_mean_value_df(df, "Average delay of all trains at departure")
    delay_bigger_than_sixty = get_mean_value_df(df, "Number of trains delayed > 60min")

    dic = {
        "Average journey time": round(mean_journey_time, 2),
        "Average delay": round(mean_delay, 2),
        "Biggest delay cause": get_biggest_delay_cause(df),
        "delay > 60": delay_bigger_than_sixty
    }
    return dic

def extract_monthly_metrics(df, year, month):
    try:
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m", errors="coerce")
    except Exception as e:
        return {"error": f"Failed to parse dates: {e}"}

    df = df.dropna(subset=["Date"])

    filtered_df = df[(df["Date"].dt.year == year) & (df["Date"].dt.month == month)]

    if filtered_df.empty:
        return {"error": f"Aucune donnée pour {year}-{str(month).zfill(2)}"}

    result = {
        "Total scheduled trains": int(get_sum_value_df(filtered_df, "Number of cancelled trains")),
        "Cancelled trains": int(get_sum_value_df(filtered_df, "Number of cancelled trains")),
        "Cancellation rate (%)": round(
            100 * get_sum_value_df(filtered_df, "Number of cancelled trains")
            / get_sum_value_df(filtered_df, "Number of scheduled trains")
        ),
        "Average delay of all arrivals (min)": round(get_mean_value_df(filtered_df, "Average delay of all trains at arrival"), 2),
    }

    return result
