"""
components/styles.py
--------------------
Estilos CSS personalizados para la interfaz gráfica de CyberWave / RadioMath.
"""

import streamlit as st


def cargar_estilos_custom():
    """Inyecta CSS personalizado en la aplicación de Streamlit."""
    st.markdown(
        """
    <style>
        /* Fondo general */
        .stApp {
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Títulos principales */
        .main-title {
            text-align: center;
            font-family: 'Courier New', monospace;
            color: #38bdf8;
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: 2px;
            text-shadow: 0 0 12px rgba(56, 189, 248, 0.6);
            margin-bottom: 0px;
        }
        
        .sub-title {
            text-align: center;
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 25px;
        }

        /* Encabezados de las tres columnas (Radios) */
        .emisor-header {
            color: #4ade80;
            font-weight: 700;
            border-bottom: 2px solid #4ade80;
            padding-bottom: 6px;
            margin-bottom: 15px;
        }
        
        .receptor-header {
            color: #f43f5e;
            font-weight: 700;
            border-bottom: 2px solid #f43f5e;
            padding-bottom: 6px;
            margin-bottom: 15px;
        }
        
        .hacker-header {
            color: #38bdf8;
            font-weight: 700;
            border-bottom: 2px solid #38bdf8;
            padding-bottom: 6px;
            margin-bottom: 15px;
        }

        /* Ajustes de botones */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.2s ease-in-out;
        }

        /* Ocultar elementos nativos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
        unsafe_allow_html=True,
    )
    