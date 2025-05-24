# Train Delay Analysis & Prediction

**A data science project to explore, analyze, and predict train delays, with an interactive Streamlit dashboard.**  
This repo contains the full pipeline: from data cleaning and analysis to deploying a user-friendly app for insights and predictions.

---

## Project Structure

```
train-delay-project/
├── bonus/                  # Visualisation des dictionnaires
├── README.md               # Documentation File
└── requirements.txt        # Dependencies list
└── read_file.py            # Read file and cleans it, beta version of tardis_eda.ipynb
└── tardis_eda.ipynb        # Read file and cleans it, write into cleaned_dataset.csv
└── tardis_model.ipynb      # Make prediction with a prediction model with the data processed with tardis_eda
```

---

## Données attendues

Le fichier `cleaned_dataset.csv` doit contenir au minimum :
- Nom des stations
- Données horaires (durée trajet, retard)
- Pourcentages par cause de retard
- Colonne `Month` pour les graphiques temporels

## Dépendances

```python
import streamlit as st
from st_circular_progress import CircularProgress
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
```

## Dashboard UX

Goal: build an interface that's **intuitive, visual, and easy to use**.  
Designed to be accessible even for non-technical users.

---

## Home

#### Top 3 des stations par données

Permet de voir des statistiques de base sur les données récupérées tel que le retard moyen, le plus de trains programmés etc.

#### Extraction de données clés

Permet de voir le temps de trajet moyen, le temps de retard moyen mais également l'intégration d'un langage de prédiction pour reconnaître le temps de retard moyen

#### Causes des délais.

Ajout d'une matrice de corrélation des délais et l'affichage de la plus grande cause de retard

## Infos sur les stations

Permet de retrouver des données triées par station telles que :

#### Données exprimées en pourcentage

- Pourcentage de trains uniquement nationaux
- Pourcentage de trains maintenus
- Plus grande cause de retard

#### Moyennes

Moyennes de retard et moyenne de temps de trajet

## Trajets entre deux stations

#### Affichage du trajet

Le trajet est affiché sur une carte avec la génération d'un pseudo trajet

#### Statistiques

Affichage du temps de trajet moyen et du retard en moyenne

#### Graphique évolutif

Permet d'afficher l'évolution du retard moyen sur cette ligne tous les mois

## Données par date

#### Statistiques basiques

Permet d'afficher :

- Les trains programmés
- Les trains annulés
- Le retard moyen

Et affiche l'évolution depuis le mois dernier

Affichage circulaire du pourcentage du taux d'annulation

## Gestion du multilingue

Tous les labels et titres s’adaptent selon la langue sélectionnée.

---


Ce module est développé dans le cadre du projet **Tardis** à EPITECH Strasbourg.


## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit app
streamlit run l'app_qui_arrive_fort
```

---

## Contact

Got ideas, feedback, or bugs to report? That's great! You can think about it a lot and keep it to **yourself**!

---
