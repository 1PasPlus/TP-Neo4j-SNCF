from neo4j import GraphDatabase

# URI et informations d'authentification de la base de données Neo4j
URI = "bolt://44.206.225.167:7687"
AUTH = ("neo4j", "realinements-bonds-opinion")

# Fonction pour obtenir les trajets directs et indirects entre deux villes
def find_trains(departure_city, arrival_city):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            
            # Requête Cypher
            direct_query = """
                MATCH (departure:Gare {name: $departure_city})-[:TRAIN]->(arrival:Gare {name: $arrival_city})
                RETURN departure, arrival
            """
            direct_result = session.run(direct_query, departure_city=departure_city, arrival_city=arrival_city)
            direct_trains = [(record["departure"]["name"], record["arrival"]["name"]) for record in direct_result]

            # Requête Cypher 
            indirect_query = """
                MATCH path = allShortestPaths((departure:Gare {name: $departure_city})-[:TRAIN*]->(arrival:Gare {name: $arrival_city}))
                WHERE length(path) > 1
                RETURN nodes(path)[1..-1] AS intermediate_stations
            """
            indirect_result = session.run(indirect_query, departure_city=departure_city, arrival_city=arrival_city)
            
            #On récup la liste des trajets intermédiaires et les infos 
            indirect_trains = []
            for record in indirect_result:
                intermediate_stations = [node["name"] for node in record["intermediate_stations"]]
                indirect_trains.append((departure_city, intermediate_stations, arrival_city))

            return direct_trains, indirect_trains


# Fonction pour afficher les résultats
def display_results(direct_trains, indirect_trains):
    print("Trajets directs :")
    if direct_trains:
        for departure, arrival in direct_trains:
            print(f"- {departure} -> {arrival}")
    else:
        print("Aucun trajet direct trouvé.")

    print("\nTrajets indirects avec correspondance :")
    if indirect_trains:
        for departure, transfer, arrival in indirect_trains:
            print(f"- {departure} -> {transfer} -> {arrival}")
    else:
        print("Aucun trajet indirect trouvé.")

# Demander à l'utilisateur de saisir les villes de départ et d'arrivée
departure_city = input("Ville de départ : ")
arrival_city = input("Ville d'arrivée : ")

# Trouver les trajets
direct_trains, indirect_trains = find_trains(departure_city, arrival_city)

# Afficher les résultats
display_results(direct_trains, indirect_trains)
