# sistema_biometrico.py
from multiprocessing import Process, Pipe, Queue, set_start_method
import time
import datetime
from collections import deque
import statistics
import hashlib
import json
import os

#--------- RUTA DEL ARCHIVO ---------
blockchain_path = "blockchain.json"

# ---------- ANALIZADORES ----------
def analizador(nombre, conn, salida):
    ventana = deque(maxlen=30)

    while True:
        try:
            data = conn.recv()
            if data == "FIN":
                break

            timestamp = data["timestamp"]

            if nombre == "frecuencia":
                valor = data["frecuencia"]
            elif nombre == "presion":
                valor = (data["presion"][0] + data["presion"][1]) / 2
            elif nombre == "oxigeno":
                valor = data["oxigeno"]
            else:
                continue

            ventana.append(valor)

            if len(ventana) >= 2:
                media = round(statistics.mean(ventana), 2)
                desv = round(statistics.stdev(ventana), 2)
            else:
                media = valor
                desv = 0.0

            resultado = {
                "tipo": nombre,
                "timestamp": timestamp,
                "media": media,
                "desv": desv
            }

            salida.put(resultado)

        except EOFError:
            break

# ---------- VERIFICADOR ----------
def calcular_hash(prev_hash, datos, timestamp):
    texto = prev_hash + json.dumps(datos, sort_keys=True) + timestamp
    return hashlib.sha256(texto.encode()).hexdigest()

def verificador(queue_f, queue_p, queue_o):
    blockchain = []
    prev_hash = "0"
    bloque_idx = 0

    while True:
        res_f = queue_f.get()
        res_p = queue_p.get()
        res_o = queue_o.get()

        if res_f == "FIN" or res_p == "FIN" or res_o == "FIN":
            break

        timestamp = res_f["timestamp"]

        alerta = False
        if res_f["media"] >= 200:
            alerta = True
        if not (90 <= res_o["media"] <= 100):
            alerta = True
        if res_p["media"] >= 200:
            alerta = True

        datos = {
            "frecuencia": {"media": res_f["media"], "desv": res_f["desv"]},
            "presion": {"media": res_p["media"], "desv": res_p["desv"]},
            "oxigeno": {"media": res_o["media"], "desv": res_o["desv"]}
        }

        nuevo_bloque = {
            "timestamp": timestamp,
            "datos": datos,
            "alerta": alerta,
            "prev_hash": prev_hash
        }

        nuevo_bloque["hash"] = calcular_hash(prev_hash, datos, timestamp)

        blockchain.append(nuevo_bloque)
        prev_hash = nuevo_bloque["hash"]

        # Guardar en blockchain.json
        try:
            with open(blockchain_path, "w") as f:
                json.dump(blockchain, f, indent=4)
            print(" 💾 Bloque guardado en blockchain.json")
        except Exception as e:
            print(f" ❌ Error al guardar el bloque: {e}")

        # Mostrar resumen
        print(f"\n[🔗 BLOQUE {bloque_idx}] Hash: {nuevo_bloque['hash']}")
        if alerta:
            print(" ⚠️  ALERTA detectada en los datos.")
        else:
            print(" ✅  Datos dentro de parámetros normales.")
        bloque_idx += 1

# ---------- GENERADOR PRINCIPAL ----------
def generador(envios):
    for i in range(5):
        paquete = {
            "timestamp": datetime.datetime.now().isoformat(timespec='seconds'),
            "frecuencia": 80 + i,
            "presion": [120 + i, 80 + i],
            "oxigeno": 98 - i
        }
        print(f"[GENERADOR] Enviando muestra {i+1}")
        for conn in envios:
            conn.send(paquete)
        time.sleep(1)

    for conn in envios:
        conn.send("FIN")

# ---------- MAIN ----------
if __name__ == "__main__":
    set_start_method("fork")  # importante para UNIX

    # Pipes para cada analizador
    parent_f, child_f = Pipe()
    parent_p, child_p = Pipe()
    parent_o, child_o = Pipe()

    # Queues para resultados
    queue_f = Queue()
    queue_p = Queue()
    queue_o = Queue()

    # Procesos analizador
    proc_f = Process(target=analizador, args=("frecuencia", child_f, queue_f))
    proc_p = Process(target=analizador, args=("presion", child_p, queue_p))
    proc_o = Process(target=analizador, args=("oxigeno", child_o, queue_o))

    # Proceso verificador
    proc_v = Process(target=verificador, args=(queue_f, queue_p, queue_o))

    # Lanzar procesos
    proc_f.start()
    proc_p.start()
    proc_o.start()
    proc_v.start()

    # Generador principal
    generador([parent_f, parent_p, parent_o])

    # Finalizar verificadores
    queue_f.put("FIN")
    queue_p.put("FIN")
    queue_o.put("FIN")

    # Esperar finalización
    proc_f.join()
    proc_p.join()
    proc_o.join()
    proc_v.join()

    print("[SISTEMA] Todos los procesos finalizaron.")
