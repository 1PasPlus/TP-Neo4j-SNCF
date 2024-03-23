from neo4j import GraphDatabase

# URI et informations d'authentification de la base de données Neo4j
URI = "bolt://44.206.225.167:7687"
AUTH = ("neo4j", "realinements-bonds-opinion")

# Fonction pour obtenir les trajets directs et indirects entre deux villes avec heures de départ et d'arrivée
def find_trains(departure_city, arrival_city, departure_time=None, arrival_time=None):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            
            # Requête Cypher 
            direct_query = """
                MATCH (departure:Gare {name: $departure_city})-[route:TRAIN]->(arrival:Gare {name: $arrival_city})
                WHERE ($departure_time IS NULL OR route.heure_depart >= $departure_time)
                AND ($arrival_time IS NULL OR route.heure_arrivee >= $arrival_time)
                RETURN departure.name AS departure_station, route.heure_depart AS departure_time, 
                       arrival.name AS arrival_station, route.heure_arrivee AS arrival_time
                ORDER BY route.heure_depart
            """
            direct_result = session.run(direct_query, departure_city=departure_city, arrival_city=arrival_city,
                                        departure_time=departure_time, arrival_time=arrival_time)
            
            # Filtrer les trains qui partent après l'heure renseignée
            if departure_time is not None:
                direct_trains = [(record["departure_station"], record["arrival_station"], record["departure_time"], record["arrival_time"]) for record in direct_result if record["departure_time"] >= departure_time]
            else:
                direct_trains = [(record["departure_station"], record["arrival_station"], record["departure_time"], record["arrival_time"]) for record in direct_result]

            # Requête Cypher 
            indirect_query = """
                MATCH path = allShortestPaths((departure:Gare {name: $departure_city})-[:TRAIN*]->(arrival:Gare {name: $arrival_city}))
                WHERE all(station in nodes(path)[1..-1] WHERE ($departure_time IS NULL OR station.heure_depart >= $departure_time)
                AND ($arrival_time IS NULL OR station.heure_arrivee >= $arrival_time))
                RETURN nodes(path) AS stations
                ORDER BY nodes(path)[1].heure_depart
            """
            indirect_result = session.run(indirect_query, departure_city=departure_city, arrival_city=arrival_city,
                                          departure_time=departure_time, arrival_time=arrival_time)
            
            #On récup la liste des trajets intermédiaires et les infos 
            indirect_trains = []
            for record in indirect_result:
                stations = record["stations"]
                intermediate_stations = [(node["name"], node["heure_depart"], node["heure_arrivee"]) for node in stations[1:-1]]
                departure_station = stations[0]["name"]
                arrival_station = stations[-1]["name"]
                intermediate_stations = [(name, dep_time, arr_time) for name, dep_time, arr_time in intermediate_stations if dep_time >= departure_time]
                
                # Filtrer les stations intermédiaires
                if intermediate_stations:
                    indirect_trains.append((departure_station, arrival_station, intermediate_stations))

            return direct_trains, indirect_trains


# Fonction pour afficher les résultats
def display_results(direct_trains, indirect_trains):
    print("Trajets directs :")
    if direct_trains:
        for departure, arrival, departure_time, arrival_time in direct_trains:
            print(f"- {departure} ({departure_time}) -> {arrival} ({arrival_time})")
    else:
        print("Aucun trajet direct trouvé.")

    print("\nTrajets indirects avec correspondance :")
    if indirect_trains:
        for departure, arrival, intermediate_stations in indirect_trains:
            intermediate_stations_str = " -> ".join([f"{station} ({dep_time} - {arr_time})" for station, dep_time, arr_time in intermediate_stations])
            print(f"- {departure} -> {intermediate_stations_str} -> {arrival}")
    else:
        print("Aucun trajet indirect trouvé.")

departure_city = input("Ville de départ : ")
arrival_city = input("Ville d'arrivée : ")
departure_time_input = input("Heure de départ souhaitée (format HH:MM) ou laisser vide : ")
departure_time = departure_time_input if departure_time_input else None
arrival_time_input = input("Heure d'arrivée souhaitée (format HH:MM) ou laisser vide : ")
arrival_time = arrival_time_input if arrival_time_input else None

# Trouver les trajets
direct_trains, indirect_trains = find_trains(departure_city, arrival_city, departure_time, arrival_time)

# Afficher les résultats
display_results(direct_trains, indirect_trains)
