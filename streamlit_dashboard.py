#!/usr/bin/env python3
"""
Dashboard Streamlit avec feux tricolores - Version classe
"""

import streamlit as st


class TrafficLightDashboard:
    """
    Classe pour afficher des feux tricolores dans Streamlit
    """

    def display_traffic_light(self, status):
        """
        Affiche un feu tricolore selon le statut

        Args:
            status (str): 'OK' = Vert, 'WARNING' = Jaune, 'DANGER' = Rouge
        """
        if status == 'OK':
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #00FF00; border: 2px solid #333;"></div>
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #444; border: 2px solid #333;"></div>
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #444; border: 2px solid #333;"></div>
                <span style="font-size: 18px; font-weight: bold; color: #00FF00;">🟢 OK</span>
            </div>
            """, unsafe_allow_html=True)

        elif status == 'WARNING':
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #444; border: 2px solid #333;"></div>
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #FFD700; border: 2px solid #333;"></div>
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #444; border: 2px solid #333;"></div>
                <span style="font-size: 18px; font-weight: bold; color: #FFD700;">🟡 WARNING</span>
            </div>
            """, unsafe_allow_html=True)

        elif status == 'DANGER':
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #444; border: 2px solid #333;"></div>
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #444; border: 2px solid #333;"></div>
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #FF0000; border: 2px solid #333;"></div>
                <span style="font-size: 18px; font-weight: bold; color: #FF0000;">🔴 DANGER</span>
            </div>
            """, unsafe_allow_html=True)

    def display_status_color(self, status_ok):
        """
        Fonction simple qui convertit boolean en feu tricolore

        Args:
            status_ok (bool): True = Vert (OK), False = Rouge (DANGER)
        """
        if status_ok:
            self.display_traffic_light('DANGER')
        else:
            self.display_traffic_light('OK')

    def show_demo(self):
        """
        Affiche une démonstration des feux tricolores
        """
        st.title("🚦 Dashboard avec Feux Tricolores")

        st.subheader("Tests des différents états:")

        st.write("**État OK (Vert):**")
        self.display_traffic_light('OK')

        st.write("**État WARNING (Jaune):**")
        self.display_traffic_light('WARNING')

        st.write("**État DANGER (Rouge):**")
        self.display_traffic_light('DANGER')

        st.markdown("---")
        st.subheader("Test avec boolean:")

        st.write("**True → Vert:**")
        self.display_status_color(True)

        st.write("**False → Rouge:**")
        self.display_status_color(False)


if __name__ == "__main__":
    # Test de la classe
