import math
import random
import time
import requests
from colorama import init, Fore, Style

# Inicializar Colorama (soporte para Windows/Linux/Mac)
init(autoreset=True)

class NeuronaAtacante:
    def __init__(self, num_entradas=3):
        self.pesos = [random.uniform(-1, 1) for _ in range(num_entradas)]
        self.bias = random.uniform(-1, 1)
        self.tasa_aprendizaje = 0.4

    def _sigmoide(self, z):
        z_clamped = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z_clamped))

    def _derivada_sigmoide(self, y):
        return y * (1.0 - y)

    def predecir(self, entradas):
        suma_z = sum(w * x for w, x in zip(self.pesos, entradas)) + self.bias
        return self._sigmoide(suma_z)

    def entrenar(self, entradas, objetivo_esperado):
        prediccion = self.predecir(entradas)
        error = objetivo_esperado - prediccion
        delta = error * self._derivada_sigmoide(prediccion)

        for i in range(len(self.pesos)):
            self.pesos[i] += self.tasa_aprendizaje * delta * entradas[i]
        self.bias += self.tasa_aprendizaje * delta

        return error, prediccion

PAYLOADS_PRUEBA = [
    {"endpoint": "/control", "params": {}},                        
    {"endpoint": "/control", "params": {"state": "0"}},            
    {"endpoint": "/inexistente", "params": {"state": "1"}},        
    {"endpoint": "/control", "params": {"state": "invalid"}},      
    {"endpoint": "/control", "params": {"state": "1"}},            
]

def extraer_features(response):
    if response is None:
        return [0.0, 0.0, 0.0]

    x1 = 1.0 if response.status_code == 200 else 0.0
    x2 = min(len(response.text) / 100.0, 1.0)
    x3 = 1.0 if '"led_state": 1' in response.text or '"led_state":1' in response.text else 0.0

    return [x1, x2, x3]

def mostrar_banner():
    print(Fore.CYAN + Style.BRIGHT + """
    ┌──────────────────────────────────────────────────────────┐
    │  🧠 NEURONA DIGITAL vs ESP32-CAM (IoT HACKING DEMO)      │
    │  Explotación de Vulnerabilidades mediante Perceptrón    │
    └──────────────────────────────────────────────────────────┘
    """)

def ejecutar_exploit(ip_esp32):
    url_base = f"http://{ip_esp32}"
    neurona = NeuronaAtacante(num_entradas=3)

    mostrar_banner()
    print(f"{Fore.YELLOW}🎯 Objetivo:{Style.RESET_ALL} {url_base}")
    print(f"{Fore.YELLOW}⚙️  Pesos iniciales de la neurona:{Style.RESET_ALL} {[round(p, 3) for p in neurona.pesos]}\n")

    éxito = False
    intentos = 0

    while not éxito and intentos < 20:
        intentos += 1
        print(f"{Fore.BLUE}{Style.BRIGHT}────────────────── [ INTENTO #{intentos} ] ──────────────────")

        payload = random.choice(PAYLOADS_PRUEBA)
        target_url = url_base + payload["endpoint"]

        try:
            print(f"{Fore.WHITE}📡 Probando vector: {Fore.CYAN}{payload['endpoint']} {Fore.MAGENTA}{payload['params']}")
            res = requests.get(target_url, params=payload["params"], timeout=3)
            
            entradas = extraer_features(res)
            objetivo_real = 1.0 if (res.status_code == 200 and '"led_state": 1' in res.text) else 0.0

            error, prediccion = neurona.entrenar(entradas, objetivo_real)

            # Formatear la salida con colores según la certeza
            porcentaje = prediccion * 100
            color_confianza = Fore.GREEN if porcentaje > 70 else (Fore.YELLOW if porcentaje > 30 else Fore.RED)

            print(f"   📥 Inputs Extraídos [x1, x2, x3]: {Fore.LIGHTWHITE_EX}{entradas}")
            print(f"   📊 Confianza de la Neurona: {color_confianza}{porcentaje:.2f}%")
            print(f"   📉 Error en la iteración: {Fore.LIGHTBLACK_EX}{error:.4f}")

            # 2. En el bucle principal (reemplaza la condición de éxito):
            if objetivo_real == 1.0:
                # Si la neurona logra el objetivo, le damos un refuerzo y detenemos
                print("\n" + Fore.GREEN + Style.BRIGHT + "═" * 60)
                print(" 🎉 ¡EXPLOIT CONFIRMADO! LA NEURONA IDENTIFICÓ EL VECTOR CORRECTO")
                print(" 💡 EL LED DEL ESP32-CAM QUEDA ENCENDIDO EN MESA")
                print("═" * 60)
                éxito = True

        except requests.exceptions.RequestException as e:
            print(f"   {Fore.RED}❌ Error de conexión:{Style.RESET_ALL} {e}")

        time.sleep(1.2)

if __name__ == "__main__":
    IP_OBJETIVO = "192.168.1.33"  # Cambia por la IP del ESP32-CAM
    ejecutar_exploit(IP_OBJETIVO)