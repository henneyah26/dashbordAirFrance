# -*- coding: utf-8 -*-
"""
Génère dataset.csv : reprend les données réelles fournies (dataset_original.csv)
et les enrichit (plus d'avions, plus de types, plus de mois, quelques anomalies
volontaires) pour donner du corps aux KPIs, filtres et au module de nettoyage.
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ---- 1. Charger les données réelles fournies par l'utilisateur ----
base = pd.read_csv("dataset_original.csv")

# ---- 2. Référentiels pour la génération synthétique complémentaire ----
types_avion = ["A320-200", "A350-900", "B777-300", "B787-9"]
immat_by_type = {
    "A320-200": ["F-GKXA", "F-GKXB", "F-GKXC", "F-GKXD"],
    "A350-900": ["F-HTYA", "F-HTYB", "F-HTYC", "F-HTYH", "F-HTYI", "F-HTYK", "F-HTYM", "F-HTYR", "F-HTYT"],
    "B777-300": ["F-GSQA", "F-GSQB", "F-GSQC"],
    "B787-9":   ["F-HRBA", "F-HRBB", "F-HRBC"],
}
composants = ["Moteur", "Avionique", "Train d'atterrissage", "Hydraulique", "Fuselage", "Cabine"]
types_maintenance = ["Preventive", "Corrective", "Inspection", "AOG"]
techniciens = [
    "Marc Lefevre", "Claire Dubois", "Thomas Girard", "Amelie Rousseau",
    "Julien Moreau", "Sophie Bernard", "Nicolas Petit", "Laura Fontaine",
]
statuts = ["Termine", "En cours", "Planifie"]

commentaires_par_composant = {
    "Moteur": ["Controle periodique moteur", "Remplacement filtre a huile", "Inspection boroscopique"],
    "Avionique": ["Verification systeme de navigation", "Mise a jour logiciel FMS", "Test radar meteo"],
    "Train d'atterrissage": ["Remplacement amortisseur", "Controle pneus", "Inspection freins carbone"],
    "Hydraulique": ["Controle circuit hydraulique", "Remplacement joint", "Test pression circuit"],
    "Fuselage": ["Inspection structurale", "Controle corrosion", "Reparation revetement"],
    "Cabine": ["Maintenance sieges", "Controle eclairage cabine", "Verification oxygene passagers"],
}

def cout_base(composant, type_maintenance):
    base_cost = {"Moteur": 14000, "Avionique": 4500, "Train d'atterrissage": 9000,
                 "Hydraulique": 5000, "Fuselage": 7000, "Cabine": 2500}[composant]
    mult = {"Preventive": 0.8, "Corrective": 1.4, "Inspection": 0.5, "AOG": 2.0}[type_maintenance]
    return max(300, np.random.normal(base_cost * mult, base_cost * 0.25))

def duree_base(composant, type_maintenance):
    base_h = {"Moteur": 10, "Avionique": 5, "Train d'atterrissage": 8,
              "Hydraulique": 6, "Fuselage": 9, "Cabine": 3}[composant]
    mult = {"Preventive": 0.8, "Corrective": 1.3, "Inspection": 0.4, "AOG": 1.8}[type_maintenance]
    return max(1, np.random.normal(base_h * mult, base_h * 0.3))

rows = []
start_date = datetime(2025, 6, 1)
next_id = int(base["id"].max()) + 1

for _ in range(320):
    type_avion = random.choice(types_avion)
    immat = random.choice(immat_by_type[type_avion])
    composant = random.choice(composants)
    type_maint = random.choices(types_maintenance, weights=[0.4, 0.3, 0.22, 0.08])[0]
    technicien = random.choice(techniciens)
    statut = random.choices(statuts, weights=[0.7, 0.15, 0.15])[0]
    jours_offset = random.randint(0, 210)
    date = start_date + timedelta(days=jours_offset)
    duree = round(duree_base(composant, type_maint), 1)
    cout = round(cout_base(composant, type_maint), 0)
    commentaire = random.choice(commentaires_par_composant[composant])

    rows.append({
        "id": next_id,
        "immatriculation": immat,
        "type_avion": type_avion,
        "type_maintenance": type_maint,
        "composant": composant,
        "date": date.strftime("%Y-%m-%d"),
        "technicien": technicien,
        "duree_heures": duree,
        "cout": cout,
        "statut": statut,
        "commentaire": commentaire,
    })
    next_id += 1

synth = pd.DataFrame(rows)

# le dataset original n'a que des A350-900 -> on l'ajoute tel quel
base_aligned = base.copy()
full = pd.concat([base_aligned, synth], ignore_index=True)

# ---- 3. Injection d'anomalies volontaires (pour la démo du nettoyage) ----
df = full.copy()
n = len(df)

# 3.1 Doublons (répéter 8 lignes)
dupes = df.sample(8, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# 3.2 Valeurs manquantes
for col, frac in [("technicien", 0.03), ("cout", 0.02), ("duree_heures", 0.02), ("composant", 0.015)]:
    idx = df.sample(frac=frac, random_state=hash(col) % 1000).index
    df.loc[idx, col] = np.nan

# 3.3 Formats de date incohérents
idx_dates = df.sample(frac=0.08, random_state=7).index
def scramble_date(d):
    try:
        dt = pd.to_datetime(d)
    except Exception:
        return d
    fmt = random.choice(["%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%d.%m.%Y"])
    return dt.strftime(fmt)
df.loc[idx_dates, "date"] = df.loc[idx_dates, "date"].apply(scramble_date)

# 3.4 Incohérences de casse / espaces sur le texte
idx_case = df.sample(frac=0.06, random_state=11).index
df.loc[idx_case, "type_maintenance"] = df.loc[idx_case, "type_maintenance"].str.lower()
idx_space = df.sample(frac=0.05, random_state=12).index
df.loc[idx_space, "technicien"] = " " + df.loc[idx_space, "technicien"].astype(str) + "  "
idx_comp_case = df.sample(frac=0.05, random_state=13).index
df.loc[idx_comp_case, "composant"] = df.loc[idx_comp_case, "composant"].str.upper()

# 3.5 Valeurs aberrantes (outliers)
idx_out_cost = df.sample(frac=0.015, random_state=21).index
df.loc[idx_out_cost, "cout"] = df.loc[idx_out_cost, "cout"] * 12
idx_out_dur = df.sample(frac=0.015, random_state=22).index
df.loc[idx_out_dur, "duree_heures"] = df.loc[idx_out_dur, "duree_heures"] * 9
idx_neg = df.sample(frac=0.01, random_state=23).index
df.loc[idx_neg, "duree_heures"] = -abs(df.loc[idx_neg, "duree_heures"])

# mélanger l'ordre
df = df.sample(frac=1, random_state=99).reset_index(drop=True)
df["id"] = range(1, len(df) + 1)

df.to_csv("dataset.csv", index=False)
print(f"dataset.csv genere : {len(df)} lignes (avec anomalies volontaires)")
print(df.isnull().sum())
