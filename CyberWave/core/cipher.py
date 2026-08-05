"""
core/cipher.py
--------------
Módulo que contiene la lógica pura de cifrado y descifrado por modulación de ondas.
"""

import math
from typing import List, Tuple, Optional

# Alfabeto modular: Caracteres ASCII imprimibles (espacio ' ' hasta '~')
ASCII_MIN: int = 32
ASCII_MAX: int = 126
N: int = ASCII_MAX - ASCII_MIN + 1  # Espacio modular N = 95


def mod_inverse(a: int, m: int = N) -> Optional[int]:
    """Calcula el inverso multiplicativo modular de 'a' módulo 'm' (a^-1 mod m).
    
    Retorna None si 'a' y 'm' no son coprimos.
    """
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def text_to_ascii_normalized(text: str) -> List[int]:
    """Convierte una cadena de texto a una lista de enteros en el rango [0, N-1]."""
    return [ord(char) - ASCII_MIN for char in text]


def ascii_normalized_to_text(numbers: List[int]) -> str:
    """Convierte una lista de enteros en el rango [0, N-1] de vuelta a una cadena de texto."""
    return "".join(chr(val + ASCII_MIN) for val in numbers)


def cifrar_mensaje(
    texto: str, a: int, b: int, k: int
) -> Tuple[str, List[int], List[int]]:
    """Cifra un texto plano aplicando una modulación afín-senoidal.

    Fórmula: C(x) = (a * m_x + b + floor(k * sin(x))) mod N

    Args:
        texto: El mensaje en texto plano a cifrar.
        a: Factor multiplicativo (debe ser coprimo con N=95).
        b: Desplazamiento lineal (Shift).
        k: Amplitud de la modulación de onda sinoidal.

    Returns:
        Tuple con:
            - texto_cifrado (str)
            - puntos_onda_original (List[int]): Valores ASCII limpios para graficar.
            - puntos_onda_cifrada (List[int]): Valores de la onda cifrada para graficar.
    
    Raises:
        ValueError: Si 'a' no es coprimo con N.
    """
    if mod_inverse(a, N) is None:
        raise ValueError(f"El valor a={a} no es coprimo con el tamaño del alfabeto N={N}.")

    puntos_orig: List[int] = text_to_ascii_normalized(texto)
    puntos_cif: List[int] = []
    texto_cif_chars: List[str] = []

    for x, val_m in enumerate(puntos_orig):
        # Componente de la onda de radio
        componente_onda = math.floor(k * math.sin(x))
        
        # Ecuación modular de cifrado
        val_c = (a * val_m + b + componente_onda) % N

        puntos_cif.append(val_c)
        texto_cif_chars.append(chr(val_c + ASCII_MIN))

    return "".join(texto_cif_chars), puntos_orig, puntos_cif


def descifrar_mensaje(texto_cifrado: str, a: int, b: int, k: int) -> str:
    """Descifra un texto aplicando la función inversa f^-1.

    Fórmula: 
        y_x = (c_x - b - floor(k * sin(x))) mod N
        m_x = (a^-1 * y_x) mod N
    """
    a_inv = mod_inverse(a, N)
    if a_inv is None:
        raise ValueError(f"No se puede descifrar: 'a={a}' no tiene inverso modular.")

    puntos_cif = text_to_ascii_normalized(texto_cifrado)
    texto_descifrado_chars: List[str] = []

    for x, val_c in enumerate(puntos_cif):
        componente_onda = math.floor(k * math.sin(x))
        
        # Deshacer desplazamiento y modulación de onda
        y_x = (val_c - b - componente_onda) % N
        
        # Deshacer multiplicación usando el inverso modular
        val_m = (a_inv * y_x) % N

        texto_descifrado_chars.append(chr(val_m + ASCII_MIN))

    return "".join(texto_descifrado_chars)