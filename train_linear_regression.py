import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def predict_next_month(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    header = lines[0].strip().split(";")
    expected_cols = len(header)
    data = [line.strip().split(";") for line in lines[1:] if len(line.strip().split(";")) == expected_cols]
    df = pd.DataFrame(data, columns=header)

    cols_to_use = [
        "Date",
        "Average journey time",
        "Number of scheduled trains",
        "Number of trains delayed at departure",
        "Average delay of late trains at departure"
    ]

    for col in cols_to_use[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=cols_to_use)
    df["Month"] = df["Date"].str.strip()
    months = sorted(df["Month"].unique())
    last_month = months[-1]
    train_data = df[df["Month"] != last_month]
    test_data = df[df["Month"] == last_month]

    X_train = train_data[[
        "Average journey time",
        "Number of scheduled trains",
        "Number of trains delayed at departure"
    ]]
    y_train = train_data["Average delay of late trains at departure"]

    X_test = test_data[[
        "Average journey time",
        "Number of scheduled trains",
        "Number of trains delayed at departure"
    ]]
    y_test = test_data["Average delay of late trains at departure"]

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    moyenne_predite = round(y_pred.mean(), 2)
    moyenne_reelle = round(y_test.mean(), 2)

    # print(f"Mois testé : {last_month}")
    # print(f"Moyenne prédite : {moyenne_predite} minutes")
    # print(f"Moyenne réelle   : {moyenne_reelle} minutes")

    #Graphique
    #plt.figure(figsize=(6, 4))
    #plt.bar(["Prédite", "Réelle"], [moyenne_predite, moyenne_reelle], color=["blue", "green"])
    #plt.title(f"Estimation du retard moyen pour le mois {last_month}")
    #plt.ylabel("Retard moyen (minutes)")
    #plt.grid(axis="y")
    #plt.show()
    dic = {"test month": last_month,
           "predict mean": moyenne_predite}
    return dic

if __name__ == "__main__":
    chemin_csv = "dataset.csv"
    predict_next_month(chemin_csv)
