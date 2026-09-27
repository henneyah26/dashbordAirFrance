# Air France — Maintenance Analytics Dashboard

Application Streamlit d'analyse des données de maintenance aéronautique.

## Structure du projet

```
air_france_maintenance_dashboard/
│
├── app.py                    # Application principale
├── generate_dataset.py       # Script de génération du dataset (déjà exécuté -> dataset.csv)
├── requirements.txt
├── dataset.csv                # Dataset utilisé par l'app (réel + enrichi, avec anomalies)
├── dataset_original.csv       # Dataset brut fourni, conservé tel quel
├── .streamlit/
│   └── config.toml            # Thème natif Streamlit
├── assets/
│   └── air_france_logo.jpg
├── utils/
│   ├── __init__.py
│   ├── auth.py                 # Authentification + session
│   ├── data_cleaning.py        # Nettoyage des données
│   ├── charts.py                # Graphiques Matplotlib / Seaborn / Plotly
│   └── icons.py                 # Icônes SVG animées (sans emoji)
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Connexion (démo)

| Identifiant  | Mot de passe   |
|--------------|----------------|
| admin        | airfrance2025  |
| technicien   | maintenance    |

*(à remplacer par une vraie authentification — LDAP/SSO/base de données — en production)*

## À propos du dataset

Le fichier `dataset_air_france.csv` fourni à l'origine (30 lignes, un seul type
d'avion, aucune anomalie) a été conservé intégralement dans `dataset_original.csv`
et intégré tel quel dans `dataset.csv`. Il a été complété par des données
synthétiques (mêmes colonnes : `id, immatriculation, type_avion,
type_maintenance, composant, date, technicien, duree_heures, cout, statut,
commentaire`) afin de couvrir plusieurs types d'avions, une plus longue période,
et de démontrer les fonctionnalités de filtrage/KPI sur un volume réaliste.

Des anomalies ont été injectées volontairement (valeurs manquantes, doublons,
formats de date multiples, casse incohérente, valeurs aberrantes) afin de
justifier le module `data_cleaning.py`, dont le rapport est visible dans
l'onglet **Données & Qualité** de l'application.

> Remarque : la colonne `aeroport` mentionnée dans le cahier des charges
> initial n'existe pas dans le dataset réel fourni — elle n'a donc pas été
> ajoutée. La heatmap "aéroport / mois" a été remplacée par une heatmap
> **composant / mois**, qui utilise les colonnes réellement disponibles.

## Fonctionnalités

- **Login** avec gestion de session (`st.session_state`)
- **Filtres** (sidebar) : période, type d'avion, composant, type de
  maintenance, technicien, statut
- **KPIs** : coût total, durée moyenne, nombre d'interventions, ratio
  corrective/préventive, coût moyen par composant, taux de conformité
- **Visualisations** : évolution des coûts, répartition par composant,
  durée moyenne par type, top techniciens, heatmap composant/mois, coût par
  avion, répartition par statut
- **Nettoyage des données** : dédoublonnage, normalisation texte/dates,
  imputation des valeurs manquantes, plafonnement des outliers (méthode IQR)
- **Design** : charte Air France (bleu `#002157`/`#0c3577`, rouge `#ee2932`),
  cartes KPI, icônes SVG animées en CSS pur (aucun emoji, aucune dépendance
  externe de type Lottie)
- **Export** des données filtrées en CSV
