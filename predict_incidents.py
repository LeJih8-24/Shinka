import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns

def predict_incidents(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    header = lines[0].strip().split(";")
    expected_cols = len(header)
    data = [line.strip().split(";") for line in lines[1:] if len(line.strip().split(";")) == expected_cols]
    df = pd.DataFrame(data, columns=header)

    df = df[[
        "Departure station",
        "Arrival station",
        "Number of trains delayed at departure",
        "Pct delay due to external causes",
        "Pct delay due to infrastructure",
        "Pct delay due to traffic management",
        "Pct delay due to rolling stock",
        "Pct delay due to passenger handling (crowding, disabled persons, connections)"
    ]]

    df = df.replace("N/A", pd.NA).dropna()
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()

    df["incident"] = (df["Number of trains delayed at departure"] > 0).astype(int)

    df["main_cause"] = df[[
        "Pct delay due to external causes",
        "Pct delay due to infrastructure",
        "Pct delay due to traffic management",
        "Pct delay due to rolling stock",
        "Pct delay due to passenger handling (crowding, disabled persons, connections)"
    ]].idxmax(axis=1)

    le_depart = LabelEncoder()
    le_arrivee = LabelEncoder()
    df["dep_encoded"] = le_depart.fit_transform(df["Departure station"])
    df["arr_encoded"] = le_arrivee.fit_transform(df["Arrival station"])

    X = df[["dep_encoded", "arr_encoded"]]
    y_incident = df["incident"]
    y_cause = df["main_cause"]
    X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(X, y_incident, test_size=0.2, random_state=42)
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_cause, test_size=0.2, random_state=42)

    model_incident = RandomForestClassifier(random_state=42)
    model_incident.fit(X_train_i, y_train_i)
    y_pred_i = model_incident.predict(X_test_i)

    model_cause = RandomForestClassifier(random_state=42)
    model_cause.fit(X_train_c, y_train_c)
    y_pred_c = model_cause.predict(X_test_c)

    print("Prédiction d'incident (0 = non, 1 = oui)")
    print(classification_report(y_test_i, y_pred_i))

    print("Prédiction de la cause principale de l'incident")
    print(classification_report(y_test_c, y_pred_c))

    cause_counts = pd.Series(y_pred_c).value_counts()
    sns.barplot(x=cause_counts.index, y=cause_counts.values)
    plt.xticks(rotation=45, ha="right")
    plt.title("Causes predites des incidents")
    plt.ylabel("Nombre de trajet")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    predict_incidents("dataset.csv")