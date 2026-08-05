"""
core/cracker.py
---------------
Módulo de criptoanálisis optimizado para la Radio Interceptora (Radio 3).
"""

from typing import List, Tuple, Dict, Any
from .cipher import N, mod_inverse, descifrar_mensaje

# Ponderación basada en la frecuencia real de caracteres en español/inglés
PESOS_CARACTERES = {
    ' ': 3.0, 'E': 2.5, 'A': 2.5, 'O': 2.0, 'S': 2.0, 'N': 1.8, 'R': 1.8,
    'I': 1.5, 'L': 1.5, 'D': 1.2, 'T': 1.2, 'U': 1.0, 'C': 1.0, 'M': 1.0,
    'e': 2.5, 'a': 2.5, 'o': 2.0, 's': 2.0, 'n': 1.8, 'r': 1.8, 'i': 1.5,
    'l': 1.5, 'd': 1.2, 't': 1.2, 'u': 1.0, 'c': 1.0, 'm': 1.0, 'Y': 1.5, 'y': 1.5
}

# Símbolos que suelen aparecer en descifrados fallidos (basura aleatoria)
SIMBOLOS_RARO_PENALIZAR = set("{}[]~^_`|\\<>&*#$%")


def evaluar_legibilidad(texto: str) -> float:
    """Calcula un puntaje de legibilidad inteligente para el texto descifrado.

    Retorna un valor de 0.0 a 100.0.
    """
    if not texto:
        return 0.0

    score = 0.0
    for char in texto:
        if char in PESOS_CARACTERES:
            score += PESOS_CARACTERES[char]
        elif char.isalnum():
            score += 0.5  # Letras normales o números
        elif char in SIMBOLOS_RARO_PENALIZAR:
            score -= 2.0  # Penalizar basura criptográfica

    # Normalizar a un porcentaje relativo al tamaño del mensaje
    max_score_teorico = len(texto) * 2.5
    porcentaje = max(0.0, min(100.0, (score / max_score_teorico) * 100.0))
    return porcentaje


def escanear_espacio_claves(texto_cifrado: str) -> Dict[str, Any]:
    """Realiza un criptoanálisis exhaustivo y preciso sobre el canal.

    Recorre sin saltos los valores válidos para garantizar encontrar la clave.
    """
    historial_claves: List[str] = []
    espectro_legibilidad: List[float] = []

    # Solo probamos valores de 'a' que tengan inverso modular válido en N=95
    valores_a_validos = [a for a in range(1, 25) if mod_inverse(a, N) is not None]
    
    mejor_puntaje: float = -1.0
    mejor_solucion: Tuple[int, int, int, str, float] = (0, 0, 0, "", 0.0)

    # Barrido completo sin saltos para no ignorar la clave exacta
    for a in valores_a_validos:
        for b in range(0, N):
            for k in range(0, 21):
                try:
                    txt_probado = descifrar_mensaje(texto_cifrado, a, b, k)
                    score = evaluar_legibilidad(txt_probado)
                except ValueError:
                    continue

                historial_claves.append(f"a:{a}|b:{b}|k:{k}")
                espectro_legibilidad.append(score)

                if score > mejor_puntaje:
                    mejor_puntaje = score
                    mejor_solucion = (a, b, k, txt_probado, score)

    return {
        "historial_claves": historial_claves,
        "espectro_legibilidad": espectro_legibilidad,
        "mejor_solucion": mejor_solucion
    }