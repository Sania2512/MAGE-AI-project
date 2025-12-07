#!/usr/bin/env python3
"""
Dashboard Streamlit avec feux tricolores automatiques.
"""

import streamlit as st
import time


class TrafficLightDashboard:
    """
    Classe pour afficher des feux tricolores dynamiques dans Streamlit.
    (Cette classe est identique à la version précédente)
    """

    def _create_light_component(self, label, color_hex, is_active):
        """Crée le code HTML pour un seul feu (allumé ou éteint)."""
        if is_active:
            light_style = f"background: radial-gradient(circle at 30% 30%, {color_hex}, {color_hex}aa); border: 2px solid #222; box-shadow: 0 0 25px {color_hex};"
            text_color = color_hex
            text_status = f"{label}"
        else:
            light_style = "background: #333; border: 2px solid #222; opacity: 0.3;"
            text_color = "#555"
            text_status = f"{label}"

        return f"""
        <div style="display: flex; flex-direction: column; align-items: center; background-color: #2c2c2c; padding: 15px; border-radius: 20px; border: 4px solid #444; width: 100px; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            <div style="width: 70px; height: 70px; border-radius: 50%; margin: 8px; {light_style}"></div>
        </div>
        <div style="text-align: center; margin-top: 10px;">
            <span style="font-size: 18px; font-weight: bold; color: {text_color};">{text_status}</span>
        </div>
        """

    def display_status_lights(self, active_status='OFF'):
        """Affiche les 3 feux dans 3 colonnes et allume celui qui correspond au statut actif."""
        col1, col2, col3 = st.columns(3)

        with col1:
            html = self._create_light_component("OK", "#00ff00", is_active=(active_status == 'OK'))
            st.markdown(html, unsafe_allow_html=True)

        with col2:
            html = self._create_light_component("WARNING", "#ffdd00", is_active=(active_status == 'WARNING'))
            st.markdown(html, unsafe_allow_html=True)

        with col3:
            html = self._create_light_component("DANGER", "#ff0000", is_active=(active_status == 'DANGER'))
            st.markdown(html, unsafe_allow_html=True)


if __name__ == "__main__":
    st.title("Tableau de Bord - Cycle Automatique")
    st.write("---")

    dashboard = TrafficLightDashboard()

    # La séquence des états que nous allons parcourir
    statuses = ('OK', 'WARNING', 'DANGER')

    # Un "placeholder" est une zone vide que nous pourrons mettre à jour
    placeholder = st.empty()

    # Index pour savoir quel état afficher
    status_index = 0

    # Boucle infinie pour l'animation
    while True:
        # Récupérer l'état actuel dans la séquence
        current_status = statuses[status_index]

        # Utiliser le placeholder pour dessiner les feux.
        # À chaque tour de boucle, le contenu du placeholder est remplacé.
        with placeholder.container():
            st.header(f"Statut Actuel : {current_status}")
            dashboard.display_status_lights(current_status)

        # Incrémenter l'index pour passer à l'état suivant
        # L'opérateur '%' (modulo) fait en sorte que l'index revienne à 0 après avoir atteint la fin de la liste
        # Le cycle sera : 0, 1, 2, 0, 1, 2, ...
        status_index = (status_index + 1) % len(statuses)

        # Faire une pause de 2 secondes
        time.sleep(2)