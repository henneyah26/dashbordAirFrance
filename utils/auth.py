# -*- coding: utf-8 -*-
"""
Authentification simple par session pour le dashboard.
En production, remplacer USERS par une vraie base (LDAP/SSO/DB) et
les mots de passe par des hachages salés stockés côté serveur.
"""
import hashlib
import streamlit as st

# username -> (sha256(password), nom affiché, rôle)
USERS = {
    "admin": (hashlib.sha256("airfrance2025".encode()).hexdigest(), "Administrateur", "admin"),
    "technicien": (hashlib.sha256("maintenance".encode()).hexdigest(), "Équipe Maintenance", "technicien"),
}


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_credentials(username: str, password: str) -> tuple[bool, str, str]:
    record = USERS.get(username.strip().lower())
    if record and record[0] == _hash(password):
        return True, record[1], record[2]
    return False, "", ""


def init_session_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.display_name = ""
        st.session_state.role = ""
        st.session_state.username = ""


def logout() -> None:
    for key in ("authenticated", "display_name", "role", "username"):
        st.session_state[key] = False if key == "authenticated" else ""


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def login(username: str, password: str) -> bool:
    ok, display_name, role = check_credentials(username, password)
    if ok:
        st.session_state.authenticated = True
        st.session_state.display_name = display_name
        st.session_state.role = role
        st.session_state.username = username.strip().lower()
    return ok
