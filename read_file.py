##                                                                                     ##
## EPITECH PROJECT - Mon, Apr, 2025                                                    ##
## Title           - tardis                                                            ##
## Description     read_files_lib, install libraries with sudo apt install python3-lib ##
##     read_file                                                                       ##

import pandas as pd
import csv
from matplotlib import pyplot as plt
import numpy as np
import sys
from bonus.dictionary_visualizer import visualiser_dictionnaire

clean_names = [
    "BORDEAUX ST JEAN",
    "LA ROCHELLE VILLE",
    "PARIS MONTPARNASSE",
    "QUIMPER",
    "TOURS",
    "ST PIERRE DES CORPS",
    "ST MALO",
    "NANTES",
    "PARIS EST",
    "STRASBOURG",
    "DUNKERQUE",
    "LILLE",
    "PARIS VAUGIRARD",
    "RENNES",
    "TOURCOING",
    "CHAMBERY CHALLES LES EAUX",
    "LYON PART DIEU",
    "MONTPELLIER",
    "MULHOUSE VILLE",
    "NICE VILLE",
    "PARIS LYON",
    "BARCELONA",
    "GENEVE",
    "MADRID",
    "BREST",
    "POITIERS",
    "TOULOUSE MATABIAU",
    "MARNE LA VALLEE",
    "MARSEILLE ST CHARLES",
    "FRANCFORT",
    "ANGOULEME",
    "METZ",
    "PARIS NORD",
    "BELLEGARDE (AIN)",
    "MACON LOCHE",
    "PERPIGNAN",
    "DOUAI",
    "VALENCE ALIXAN TGV",
    "LAUSANNE",
    "ANGERS SAINT LAUD",
    "STUTTGART",
    "LAVAL",
    "NANCY",
    "BESANCON FRANCHE COMTE TGV",
    "GRENOBLE",
    "NIMES",
    "SAINT ETIENNE CHATEAUCREUX",
    "ITALIE",
    "ZURICH",
    "VANNES",
    "ANNECY",
    "AVIGNON TGV",
    "MADRID",
    "LE MANS",
    "ST MALO",
    "ARRAS",
    "DIJON VILLE",
    "LE CREUSOT MONTCEAU MONTCHANIN",
    "REIMS",
]
def show_data(df):
    df.columns = df.columns.str.strip()
    df["Departure station"] = (
        df["Departure station"].astype(str).str.upper().str.strip()
    )
    df["Average journey time"] = pd.to_numeric(
        df["Average journey time"], errors="coerce"
    )

    df_grouped = (
        df.groupby("Departure station")["Number of cancelled trains"]
        .mean()
        .reset_index()
    )

    stations = df_grouped["Departure station"].tolist()
    delays = df_grouped["Number of cancelled trains"].tolist()

    plt.figure(figsize=(10, 6))
    plt.plot(stations, delays, marker="o")
    plt.xticks(rotation=45, ha="right")
    plt.title("Retards moyens par station de départ")
    plt.xlabel("Station")
    plt.ylabel("Retard moyen (min)")
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def get_data_station(df: pd.DataFrame):
    dic_values = {}
    temp_dic = {}
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    df_grouped = df.groupby("Departure station")[numeric_columns].mean().reset_index()
    to_csv(df_grouped, path="grouped.csv")
    for elt in df_grouped["Departure station"]:
        tab = df_grouped[df_grouped["Departure station"] == elt].iloc[0]
        for i in range(1, len(tab)):
            temp_dic[df_grouped.columns[i]] = tab[i]
        dic_values[elt] = temp_dic
    return dic_values

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

def read_csv(csv_path):
    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="utf-8",
        quoting=csv.QUOTE_NONE,
        escapechar="\\",
        on_bad_lines="skip",
        engine="python",
    )
    return df

def to_csv(df: pd.DataFrame, path="test.csv"):
    df.to_csv(path, sep=";", index=None)
def hamming_distance(s1, s2):
    if len(s1) != len(s2):
        return np.inf
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))


def get_closest_match(name, correct_list):
    if not name or not isinstance(name, str):
        return "None"

    name = name.strip().upper()
    correct_list_cleaned = [n.strip().upper() for n in correct_list]

    distances = [hamming_distance(name, ref) for ref in correct_list_cleaned]
    min_distance = min(distances)

    if min_distance <= 1:
        best_match_index = distances.index(min_distance)
        return correct_list[best_match_index]
    else:
        return "None"

def clean_data(df: pd.DataFrame):
    for column in df.columns:
        if column in ["Departure station", "Arrival station"] or "comments" in column:
            print(column)
            if column in df.columns:
                df[column] = (
                    df[column]
                    .fillna("")
                    .apply(lambda x: get_closest_match(str(x), clean_names))
                )
        elif column == "Date":
            df[column] = df[column].fillna(method='ffill')
        else:
            df[column] = df[column].fillna(0)

def main(): 
    df = read_csv("dataset.csv")
    print("Fichier lu.")

    clean_data(df)
    print("Données nettoyées.")

    to_csv(df, path="cleaned_dataset.csv")
    print("Données sauvegardées dans test.csv.")

    data_values_dic = get_data_station(df)
    data_values_tab = get_data_tab(df)
    # show_data(df)

    for elt in data_values_tab:
        for i in range(0, len(data_values_tab[elt])):
            print(f"City: {elt}", end="")
            print(
                f"{data_values_tab[elt]['Arrival stations'][i]} - {data_values_tab[elt]['Dates'][i]}"
            )


if __name__ == "__main__":
    main()