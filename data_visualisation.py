import matplotlib.pyplot as plt
import pandas as pd

def show_arrival_data(df):
    # calc retard train (15 max => + visu)
    arrival_stats = df[df['Arrival station'] != "None"].groupby('Arrival station')
    ['Average journey time'] \
                    .mean()\
                    .sort_values(ascending=False) \
                    .head(15)
                    ## mean => calc moy retards
                    ## sort_values => trie stations du retard + eleve au -
                    ## head => only les 15 first stations
    
    # creation du graph
    plt.figure(figsize=(12, 6))
    plt.plot(
        arrival_stats.index,
        arrival_stats.values,
        marker="o",
        linestyle="-",
        color='#1f77b4',
        markersize=8,
        linewidth=1.5,
    )
    # perso du graph
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 15 stations d\'arrivée par retard moyen')
    plt.xlabel('Station')
    plt.ylabel('Retard moyen (min)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def delay_probability(delay_proba):
    plt.figure(figsize=(12, 6))

    ##graphique + regression lineaire 
    sns.regplot(
        x='Distance',
        y='Delay_Probability',
        data=delay_proba,
        scatter_kws={'s' : 100, 'alpha': 0.6},
        line_kws={'color': 'red', 'linestyle': '--'}
        )
    #personnalisation
    plt.title('Probabilité de retard (>15min) en fonction de la distance', pad=20)
    plt.xlabel('Distance du trajet (groupes de 50km)')
    plt.ylabel('Probabilité de retard')
    plt.grid(True, alpha=0.3)

    # + etiquettes valeurs (met en valeur les donnees importantes)
    for i, row in delay_proba.iterrows():
        plt.text(row['Distance']+5, row['Delay_Probability'], 
            f"{row['Delay_Probability']:.0%}", 
            ha='left', va='center')

