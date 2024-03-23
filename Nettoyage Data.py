import pandas as pd

# Nettoyage des données du DataFrame
df = pd.read_csv("tgvmax.csv", header="infer", delimiter=";")
df = df.dropna()
X_trains = df.drop("Disponibilité de places MAX JEUNE et MAX SENIOR", axis=1)
df = X_trains.copy()
df.drop(df[(df['Origine'] == '') | (df['Origine'] == 'TBD')| (df['Destination'] == '')| (df['Destination'] == 'TBD')].index, inplace=True)

print(df.info())
nombre_gares_uniques = df['Origine'].nunique()

print("Nombre de gares d'origine uniques :", nombre_gares_uniques)
#302 gares et on a 302 noeud dans notre BDD

#Afin d'ajouter les liens dans notre modèle relationnel nous devons créer une nouvelle colonne Date_arrivee 
#Cette colonne sera identique à la colonne Date renomée Date_depart sauf si le train arrive le jour d'après

df['DATE'] = pd.to_datetime(df['DATE'])
df['Heure_depart'] = pd.to_datetime(df['Heure_depart'])
df['Heure_arrivee'] = pd.to_datetime(df['Heure_arrivee'])

df['Date_arrivee'] = df['DATE']

df.loc[df['Heure_depart'] > df['Heure_arrivee'], 'Date_arrivee'] += pd.Timedelta(days=1)

df = df.rename(columns={'DATE': 'Date_depart'})

# Enregistrer le DataFrame modifié dans un nouveau fichier CSV
df.to_csv("clear_tgvmax.csv", sep=";", index=False)
