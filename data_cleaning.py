# -*- coding: utf-8 -*-
"""
Module de nettoyage des données de maintenance Air France.
Toutes les fonctions sont pures (ne modifient pas le DataFrame en place)
et renvoient un rapport détaillant les corrections appliquées.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CANONICAL_MAINTENANCE = ["Preventive", "Corrective", "Inspection", "AOG"]
CANONICAL_STATUT = ["Termine", "En cours", "Planifie"]
CANONICAL_COMPOSANT = [
    "Moteur", "Avionique", "Train d'atterrissage", "Hydraulique", "Fuselage", "Cabine"
]

REQUIRED_COLUMNS = [
    "id", "immatriculation", "type_avion", "type_maintenance", "composant",
    "date", "technicien", "duree_heures", "cout", "statut", "commentaire",
]


def load_raw_data(path: str) -> pd.DataFrame:
    """Charge le CSV brut sans aucune transformation."""
    return pd.read_csv(path)


def _normalize_text_column(series: pd.Series, canonical_values: list[str]) -> pd.Series:
    """Trim + capitalisation cohérente en s'appuyant sur une liste canonique (NaN préservés)."""
    lookup = {v.lower(): v for v in canonical_values}

    def _norm(v):
        if pd.isna(v):
            return v
        v = str(v).strip()
        return lookup.get(v.lower(), v)

    return series.apply(_norm)


def _parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Parse une colonne de dates contenant plusieurs formats (JJ/MM/AAAA, AAAA/MM/JJ, etc.)."""
    def parse_one(value):
        if pd.isna(value):
            return pd.NaT
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%d.%m.%Y"):
            try:
                return pd.to_datetime(value, format=fmt)
            except (ValueError, TypeError):
                continue
        return pd.to_datetime(value, errors="coerce", dayfirst=True)

    return series.apply(parse_one)


def _cap_outliers_iqr(series: pd.Series, factor: float = 1.5) -> tuple[pd.Series, int]:
    """Plafonne les valeurs aberrantes (méthode IQR) au lieu de les supprimer."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - factor * iqr, q3 + factor * iqr
    n_outliers = int(((series < low) | (series > high)).sum())
    capped = series.clip(lower=max(low, 0), upper=high)
    return capped, n_outliers


def clean_data(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Nettoie le DataFrame brut et renvoie (df_propre, rapport).
    Étapes : dédoublonnage -> normalisation texte -> parsing dates ->
              traitement valeurs manquantes -> traitement outliers.
    """
    report = {"steps": []}
    df = df_raw.copy()

    # 1. Colonnes manquantes éventuelles
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        report["steps"].append(f"Colonnes absentes ignorées : {missing_cols}")

    # 2. Doublons métier (on ignore "id", qui est un simple compteur et ne
    #    doit pas empêcher de détecter deux lignes identiques sur le fond)
    n_before = len(df)
    dedup_subset = [c for c in df.columns if c != "id"]
    df = df.drop_duplicates(subset=dedup_subset)
    n_dupes = n_before - len(df)
    report["duplicates_removed"] = n_dupes
    report["steps"].append(f"{n_dupes} doublon(s) supprimé(s)")

    # 3. Normalisation du texte
    if "type_maintenance" in df.columns:
        df["type_maintenance"] = _normalize_text_column(df["type_maintenance"], CANONICAL_MAINTENANCE)
    if "statut" in df.columns:
        df["statut"] = _normalize_text_column(df["statut"], CANONICAL_STATUT)
    if "composant" in df.columns:
        df["composant"] = _normalize_text_column(df["composant"], CANONICAL_COMPOSANT)
    if "technicien" in df.columns:
        df["technicien"] = df["technicien"].apply(lambda v: str(v).strip() if pd.notna(v) else v)
    if "immatriculation" in df.columns:
        df["immatriculation"] = df["immatriculation"].apply(
            lambda v: str(v).strip().upper() if pd.notna(v) else v
        )
    report["steps"].append("Casse / espaces normalisés sur les colonnes texte")

    # 4. Dates hétérogènes
    if "date" in df.columns:
        df["date"] = _parse_mixed_dates(df["date"])
        n_unparsed = int(df["date"].isna().sum())
        report["steps"].append(f"Dates reformatées (formats mixtes) — {n_unparsed} non reconnue(s)")

    # 5. Durées négatives -> valeur absolue (erreur de saisie)
    if "duree_heures" in df.columns:
        df["duree_heures"] = pd.to_numeric(df["duree_heures"], errors="coerce").abs()

    if "cout" in df.columns:
        df["cout"] = pd.to_numeric(df["cout"], errors="coerce")

    # 6. Valeurs manquantes
    missing_before = df.isna().sum()
    if "technicien" in df.columns:
        df["technicien"] = df["technicien"].fillna("Non renseigné")
    if "composant" in df.columns:
        df["composant"] = df["composant"].fillna("Non renseigné")
    if "duree_heures" in df.columns:
        df["duree_heures"] = df["duree_heures"].fillna(df["duree_heures"].median())
    if "cout" in df.columns:
        df["cout"] = df["cout"].fillna(df.groupby("composant")["cout"].transform("median"))
        df["cout"] = df["cout"].fillna(df["cout"].median())
    df = df.dropna(subset=["date"]) if "date" in df.columns else df
    report["missing_before"] = int(missing_before.sum())
    report["steps"].append("Valeurs manquantes imputées (médiane / 'Non renseigné')")

    # 7. Outliers (coût / durée) — plafonnés, pas supprimés
    n_out_cost, n_out_dur = 0, 0
    if "cout" in df.columns:
        df["cout"], n_out_cost = _cap_outliers_iqr(df["cout"])
    if "duree_heures" in df.columns:
        df["duree_heures"], n_out_dur = _cap_outliers_iqr(df["duree_heures"])
    report["outliers_capped"] = n_out_cost + n_out_dur
    report["steps"].append(f"{n_out_cost + n_out_dur} valeur(s) aberrante(s) plafonnée(s)")

    # 8. Types finaux + arrondis
    df["cout"] = df["cout"].round(0)
    df["duree_heures"] = df["duree_heures"].round(1)
    df = df.sort_values("date", ascending=False).reset_index(drop=True)

    report["rows_before"] = n_before
    report["rows_after"] = len(df)
    return df, report
