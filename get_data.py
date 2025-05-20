import pandas as pd
import csv
import numpy as np

def read_csv(filename):
    final_dic = {}
    lignes_corrigees = []

    with open(filename, mode="r", encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')
        header = next(reader)
        nb_columns = len(header)

        for col in header:
            final_dic[col] = []

        buffer = ""
        for line in f:
            buffer += line
            if buffer.count(";") >= nb_columns - 1:
                try:
                    row = next(csv.reader([buffer], delimiter=";", quotechar='"'))
                    row = [val.replace('\n', ' | ').strip() for val in row]
                    if len(row) == nb_columns:
                        lignes_corrigees.append(row)
                except Exception as e:
                    if not e:
                        print(e)
                    buffer = ""
                buffer = ""

        for row in lignes_corrigees:
            for i, val in enumerate(row):
                final_dic[header[i]].append(val)
    return pd.DataFrame(final_dic)

def get_data_station(df: pd.DataFrame):
    dic_values = {}
    temp_dic = {}
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    df_grouped = df.groupby("Departure station")[numeric_columns].mean().reset_index()
    for elt in df_grouped["Departure station"]:
        tab = df_grouped[df_grouped["Departure station"] == elt].iloc[0]
        for i in range(1, len(tab)):
            temp_dic[df_grouped.columns[i]] = tab[i]
        dic_values[elt] = temp_dic
    return dic_values


####################################################

def append_to_dic(line, columns, dic, table_of_dup):
    name = line["Departure station"]
    temp_tab = [line["Date"], line["Departure station"], line["Arrival station"]]
    if name == "None" or temp_tab in table_of_dup:
        return 0
    table_of_dup.append(temp_tab)
    if name not in dic:
        dic[name] = {}
    if "Arrival stations" not in dic[name]:
        dic[name]["Arrival stations"] = []
    else:
        dic[name]["Arrival stations"].append(line["Arrival station"])
    if "Dates" not in dic[name]:
        dic[name]["Dates"] = []
    else:
        dic[name]["Dates"].append(temp_tab[0])
    for elt in columns:
        if elt not in dic[name]:
            dic[name][elt] = []
        dic[name][elt].append(line[elt])
    return 0


def get_data_tab(df: pd.DataFrame):
    dic = {}
    table = []
    df_sorted = df.sort_values("Departure station")
    numeric_columns = df_sorted.select_dtypes(include=[np.number]).columns.tolist()
    for i in range(0, len(df_sorted)):
        append_to_dic(df_sorted.iloc[i], numeric_columns, dic, table)
    return dic


def get_data_program(df: pd.DataFrame):
    data_values_dic = get_data_station(df)
    data_values_tab = get_data_tab(df)
    return data_values_dic, data_values_tab