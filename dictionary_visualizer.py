import networkx as nx
import matplotlib.pyplot as plt


# CEST IMMONDE TELLEMENT YA DE VALEURS
# après je savais pas trop quoi faire donc bon caca quoi

def visualiser_dictionnaire(dico):
    """
    Visualise un dictionnaire sous forme de graphe avec les clés et valeurs comme nœuds,
    avec un espacement personnalisé pour les dictionnaires imbriqués.

    :param dico: Le dictionnaire à visualiser.
    """

    def ajouter_dico_graphe(dico, graph, parent=None, niveau=0):
        """
        Ajoute les éléments d'un dictionnaire au graphe en respectant la hiérarchie des niveaux.
        """
        for key, value in dico.items():
            graph.add_node(key, niveau=niveau)
            if parent:
                graph.add_edge(parent, key)
            if isinstance(value, dict):
                ajouter_dico_graphe(value, graph, key, niveau + 1)
            else:
                graph.add_node(value)
                graph.add_edge(key, value)

    G = nx.Graph()

    ajouter_dico_graphe(dico, G)

    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=100)

    niveaux = nx.get_node_attributes(G, "niveau")
    pos_modifiee = {}

    for node, (x, y) in pos.items():
        if node in niveaux:
            pos_modifiee[node] = (x, y + 0.3 * niveaux[node])
        else:
            pos_modifiee[node] = (
                x,
                y,
            )

    plt.figure(figsize=(12, 10))
    nx.draw(
        G,
        pos=pos_modifiee,
        with_labels=True,
        node_size=2500,
        node_color="skyblue",
        font_size=10,
        font_weight="bold",
        edge_color="gray",
    )
    plt.title("Visualisation d'un Dictionnaire Python (Espacé)")
    plt.show()
