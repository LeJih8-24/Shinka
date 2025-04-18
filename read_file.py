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
        else:
            df[column] = df[column].fillna(0)


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


def get_data_station(df: pd.DataFrame):
    dic_values = {}
    temp_dic = {}
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    stations = df["Departure station"].tolist()
    df_grouped = df.groupby("Departure station")[numeric_columns].mean().reset_index()
    to_csv(df_grouped, path="grouped.csv")
    for elt in df_grouped["Departure station"]:
        tab = df_grouped[df_grouped["Departure station"] == elt].iloc[0]
        for i in range(1, len(tab)):
            temp_dic[df_grouped.columns[i]] = tab[i]
        dic_values[elt] = temp_dic
    return dic_values


def show_data(df):
    df.columns = df.columns.str.strip()
    df["Departure station"] = (
        df["Departure station"].astype(str).str.upper().str.strip()
    )
    df["Average journey time"] = pd.to_numeric(
        df["Average journey time"], errors="coerce"
    )

    df_grouped = (
        df.groupby("Departure station")["Average journey time"].mean().reset_index()
    )

    stations = df_grouped["Departure station"].tolist()
    delays = df_grouped["Average journey time"].tolist()

    plt.figure(figsize=(10, 6))
    plt.plot(stations, delays, marker="o")
    plt.xticks(rotation=45, ha="right")
    plt.title("Retards moyens par station de départ")
    plt.xlabel("Station")
    plt.ylabel("Retard moyen (min)")
    plt.tight_layout()
    plt.grid(True)
    plt.show()


def to_csv(df: pd.DataFrame, path="test.csv"):
    df.to_csv(path, sep=";", index=None)


def main():
    if len(sys.argv) != 2:
        print("python3 read_file.py [file]")
        exit(2)
    df = read_csv("dataset.csv")
    print("Fichier lu.")

    clean_data(df)
    print("Données nettoyées.")

    # to_csv(df)
    print("Données sauvegardées dans test.csv.")

    data_values_dic = get_data_station(df)
    print(data_values_dic)


if __name__ == "__main__":
    main()
