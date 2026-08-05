"""
components/charts.py
--------------------
Módulo de renderizado de gráficas con Plotly para las señales de radio
y el espectro de legibilidad del criptoanálisis.
"""

from typing import List
import plotly.graph_objects as go

# Configuración base de tema oscuro para las gráficas de Plotly
LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.8)",
    font=dict(color="#94a3b8", family="monospace"),
    height=230,
    margin=dict(l=20, r=20, t=35, b=20),
    xaxis=dict(showgrid=True, gridcolor="#1e293b", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#1e293b", zeroline=False, range=[0, 95]),
)


def crear_grafica_onda_limpia(puntos_orig: List[int]) -> go.Figure:
    """Genera la gráfica verde estilo osciloscopio para la Radio 1 (Emisor)."""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=list(range(len(puntos_orig))),
            y=puntos_orig,
            mode="lines+markers",
            name="Señal ASCII Base",
            line=dict(color="#4ade80", width=2),
            marker=dict(size=6, color="#4ade80", symbol="circle"),
        )
    )

    layout = LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        title=dict(text="⚡ Onda Base del Mensaje (Texto Plano)", font=dict(color="#4ade80", size=13)),
    )
    return fig


def crear_grafica_onda_cifrada(puntos_cif: List[int]) -> go.Figure:
    """Genera la gráfica caótica en rojo para el Canal / Radio 2 (Receptor)."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=list(range(len(puntos_cif))),
            y=puntos_cif,
            mode="lines",
            name="Señal Modulada",
            line=dict(color="#f43f5e", width=2),
        )
    )

    layout = LAYOUT_BASE.copy()
    fig.update_layout(
        **layout,
        title=dict(text="📡 Señal Interceptada en el Aire (Cifrada)", font=dict(color="#f43f5e", size=13)),
    )
    return fig


def crear_grafica_espectro_escaneo(puntajes: List[float]) -> go.Figure:
    """Genera la gráfica del espectro de legibilidad para la Radio 3 (Interceptor).

    Muestra el barrido del espacio de claves e identifica picos de frecuencia.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            y=puntajes,
            mode="lines",
            name="Coincidencia %",
            line=dict(color="#38bdf8", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.15)",
        )
    )

    layout = LAYOUT_BASE.copy()
    # Ajuste de escala específico para porcentaje [0-105%]
    layout["yaxis"] = dict(
        showgrid=True,
        gridcolor="#1e293b",
        range=[0, 105],
        title=dict(text="Coincidencia %", font=dict(size=10)),
    )
    layout["xaxis"] = dict(showgrid=False, title=dict(text="Combinaciones Probadas", font=dict(size=10)))

    fig.update_layout(
        **layout,
        title=dict(text="🔍 Espectro de Legibilidad (Criptoanálisis)", font=dict(color="#38bdf8", size=13)),
    )
    return fig