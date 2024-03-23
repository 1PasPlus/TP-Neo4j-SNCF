import pandas as pd
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor

#Ouverture csv nettoyer après execution de Nettoyage Data 
df = pd.read_csv("tgvmax.csv", header="infer", delimiter=";")

#On ajoute toutes les gares unique en tant que noeud dans notre BDD neo4j
URI = "bolt://44.206.225.167:7687"
AUTH = ("neo4j", "realinements-bonds-opinion")

#Fonction pour créer des relations entre les gares en utilisant les informations de votre DataFrame
def create_train_relationships(train_no, axe, entity, heure_depart, heure_arrivee, date_depart, date_arrivee, origine_iata, destination_iata):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.write_transaction(
                lambda tx: tx.run(
                    """
                    MATCH (origine:Gare {iata: $origine_iata})
                    MATCH (destination:Gare {iata: $destination_iata})
                    MERGE (origine)-[r:TRAIN {train_no: $train_no, axe: $axe, entity: $entity, heure_depart: $heure_depart, heure_arrivee: $heure_arrivee, date_depart: $date_depart, date_arrivee: $date_arrivee}]->(destination)
                    """,
                    train_no=train_no, axe=axe, entity=entity, heure_depart=str(heure_depart), heure_arrivee=str(heure_arrivee), date_depart=str(date_depart), date_arrivee=str(date_arrivee), origine_iata=origine_iata, destination_iata=destination_iata
                )
            )

# Utilisation de ThreadPoolExecutor pour exécuter les sessions en parallèle
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(create_train_relationships, row['TRAIN_NO'], row['Axe'], row['ENTITY'], row['Heure_depart'], row['Heure_arrivee'], row['Date_depart'], row['Date_arrivee'], row['Origine IATA'], row['Destination IATA']) for _, row in df.iterrows()]

    for future in futures:
        future.result()  # Attendre la fin de chaque tâche
    
