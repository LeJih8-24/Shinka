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

## Step 1: Data Exploration & Cleaning

Before any analysis, we make sure the data is fresh and clean.  
Goal: clean up the dataset, fix any weird values, and prep it for modeling.

### Tasks:
- Load and inspect the dataset
- Handle missing values and remove duplicates
- Convert columns to appropriate data types
- Feature engineering (day of the week, peak hours, etc.)

---

## Step 2: Data Visualization & Analysis

Once the data is clean, we use visualizations to detect trends and delay patterns:  
when, where, and why the trains are running late.

### Tasks:
- Generate descriptive statistics
- Visualize delay distributions (histograms, boxplots…)
- Compare delays across stations and times of day
- Use heatmaps to explore variable correlations

---

## Step 3: Prediction Model

Time to switch to Machine Learning. We use historical data to predict future delays.

### Tasks:
- Select relevant features (e.g., departure station, time, past delays)
- Train a ML model (Linear Regression, Decision Tree, Random Forest…)
- Evaluate performance (RMSE, R², accuracy…)
- Tune hyperparameters to boost performance
- Compare different models and justify the final choice

---

## Step 4: Streamlit Dashboard

Now for the star of the show: a Streamlit app to explore insights and interact with predictions in real time.

### Tasks:
- Delay distribution charts (histograms, boxplots…)
- Station-level analysis (average delays, cancellation rates)
- Heatmaps showing contributing factors (traffic, infrastructure, incidents…)
- Interactive elements: select stations, routes, dates
- Summary stats: average delays, punctuality, cancellations
- Integrated model for real-time predictions
- Deploy the app + write user documentation

---

## Dashboard UX

Goal: build an interface that's **intuitive, visual, and easy to use**.  
Designed to be accessible even for non-technical users.

---

## Coming Soon

> To be added:
> - Dataset details
> - Technical architecture
> - Local setup instructions
> - Link to the deployed app

---

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
