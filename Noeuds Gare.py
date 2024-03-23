import pandas as pd
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor

#Ouverture csv nettoyer après execution de Nettoyage Data 
df = pd.read_csv("tgvmax.csv", header="infer", delimiter=";")

#On ajoute toutes les gares unique en tant que noeud dans notre BDD neo4j
URI = "bolt://44.206.225.167:7687"
AUTH = ("neo4j", "realinements-bonds-opinion")

#Fonction pour créer des noeuds uniques pour chaque gare
def create_unique_nodes(IATA_gare, NOM_gare):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.write_transaction(
                lambda tx: tx.run(
                    
                    "MERGE (g:Gare {iata: $iata, name: $name})",
                    "ON CREATE SET g.id = apoc.create.nodeId()",
                    iata=IATA_gare, name=NOM_gare, database_="neo4j",
                )
            )

# Utilisation de ThreadPoolExecutor pour exécuter les sessions en parallèle
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(create_unique_nodes, row[4], row[6]) for _, row in df.iterrows()]

    for future in futures:
        future.result()  # Attendre la fin de chaque tâche
