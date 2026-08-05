"""
app.py
------
Punto de entrada principal para CyberWave / RadioMath.
Integra la maquetación de Streamlit en 3 columnas con el motor matemático y visual.
"""

import streamlit as st
import numpy as np

# Importaciones de paquetes locales
from core.cipher import cifrar_mensaje, mod_inverse, N
from core.cracker import escanear_espacio_claves
from components.styles import cargar_estilos_custom
from components.charts import (
    crear_grafica_onda_limpia,
    crear_grafica_onda_cifrada,
    crear_grafica_espectro_escaneo,
)

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ---------------------------------------------------------
st.set_page_config(
    page_title="CyberWave: Radio Criptográfica",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

cargar_estilos_custom()

# ---------------------------------------------------------
# 2. ENCABEZADO DE LA APLICACIÓN
# ---------------------------------------------------------
st.markdown('<div class="main-title">CYBERWAVE :: RADIO CRIPTOGRÁFICA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Demostración visual de cifrado por modulación de ondas y criptoanálisis de frecuencias</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 3. MAQUETACIÓN EN 3 COLUMNAS
# ---------------------------------------------------------
col_emisor, col_receptor, col_hacker = st.columns([1, 1, 1.2], gap="medium")

# Variables globales de estado entre columnas
a_valido = False
txt_cifrado = ""
puntos_orig = []
puntos_cif = []

# =========================================================
# COLUMNA 1: RADIO 1 (EMISOR)
# =========================================================
with col_emisor:
    st.markdown('<h3 class="emisor-header">📻 RADIO 1: EMISOR</h3>', unsafe_allow_html=True)
    
    mensaje_input = st.text_input(
        "Mensaje a transmitir:",
        value="HACKING Y MATEMATICAS",
        max_chars=40,
        help="Texto plano que se transformará en señal.",
    )
    
    st.caption("⚙️ **Parámetros de la Clave (Frecuencia):**")
    clave_a = st.slider("Factor multiplicador (a)", min_value=1, max_value=25, value=7, step=1)
    clave_b = st.slider("Desplazamiento / Shift (b)", min_value=0, max_value=94, value=15)
    clave_k = st.slider("Amplitud de onda sinoidal (k)", min_value=0, max_value=20, value=10)

    # Validar coprimicidad de 'a'
    if mod_inverse(clave_a, N) is None:
        st.error(f"⚠️ 'a={clave_a}' no es coprimo con N={N}. Elige otro número (ej. 3, 7, 11).")
        a_valido = False
    else:
        a_valido = True

    if mensaje_input and a_valido:
        txt_cifrado, puntos_orig, puntos_cif = cifrar_mensaje(
            mensaje_input, clave_a, clave_b, clave_k
        )
        
        # Gráfica de la onda limpia
        fig_orig = crear_grafica_onda_limpia(puntos_orig)
        st.plotly_chart(fig_orig, use_container_width=True)


# =========================================================
# COLUMNA 2: RADIO 2 (RECEPTOR AUTORIZADO)
# =========================================================
with col_receptor:
    st.markdown('<h3 class="receptor-header">📡 CANAL / RADIO 2</h3>', unsafe_allow_html=True)
    
    if mensaje_input and a_valido:
        # Gráfica de la onda caótica cifrada
        fig_cif = crear_grafica_onda_cifrada(puntos_cif)
        st.plotly_chart(fig_cif, use_container_width=True)

        st.markdown("**Texto en la Señal Interceptada:**")
        st.code(txt_cifrado, language="text")

        btn_descifrar = st.button("🔓 Descifrar con Clave Compartida")
        if btn_descifrar:
            st.success(f"**Mensaje Reconstruido por Radio 2:**\n`{mensaje_input}`")
    else:
        st.info("Esperando una señal válida en el emisor...")


# =========================================================
# COLUMNA 3: RADIO 3 (INTERCEPTOR / HACKER)
# =========================================================
with col_hacker:
    st.markdown('<h3 class="hacker-header">👾 RADIO 3: INTERCEPTOR</h3>', unsafe_allow_html=True)
    st.caption("🕵️ Escáner Criptoanalítico de Frecuencia")

    btn_escaneo = st.button("⚡ Iniciar Escaneo Exhaustivo de Señal")

    # Contenedores dinámicos para actualización en pantalla
    ph_status = st.empty()
    ph_chart = st.empty()
    ph_result = st.empty()

    if btn_escaneo and mensaje_input and a_valido:
        ph_status.info("🔍 Barriendo espacio de claves en el canal público...")

        # Ejecutar el criptoanálisis desde el módulo core/cracker.py
        # Usamos paso_b=2 para agilizar el renderizado interactivo
        res_hack = escanear_espacio_claves(txt_cifrado)
        
        espectro = res_hack["espectro_legibilidad"]
        a_h, b_h, k_h, txt_h, score_h = res_hack["mejor_solucion"]

        # Renderizar la gráfica del espectro de legibilidad
        fig_scan = crear_grafica_espectro_escaneo(espectro)
        ph_chart.plotly_chart(fig_scan, use_container_width=True)

        # Mostrar estado de éxito
        ph_status.success(f"🎯 **¡Sincronización Exitosa! (Legibilidad: {score_h:.1f}%)**")
        
        ph_result.markdown(f"""
        ---
        **🔑 Clave Matemáticamente Deducida:**
        * $a = {a_h}$
        * $b = {b_h}$
        * $k = {k_h}$
        
        **💬 Texto Reconstruido en Tiempo Real:**
        ```text
        {txt_h}
        ```
        """)