# sistema_biometrico.py
from multiprocessing import Process, Pipe, Queue
import time
import datetime

# ---------- ANALIZADORES ----------
def analizador(nombre, conn, salida):
    while True:
        try:
            data = conn.recv()
            if data == "FIN":
                break
            print(f"[{nombre}] Recibido:", data)
            resultado = {"tipo": nombre, "timestamp": data["timestamp"], "resultado": 0}
            salida.put(resultado)
        except EOFError:
            break

# ---------- VERIFICADOR ----------
def verificador(queue_f, queue_p, queue_o):
    while True:
        res_f = queue_f.get()
        res_p = queue_p.get()
        res_o = queue_o.get()
        if res_f == "FIN" or res_p == "FIN" or res_o == "FIN":
            break
        print(f"[VERIFICADOR] Resultados recibidos:")
        print(" - Frecuencia:", res_f)
        print(" - Presión   :", res_p)
        print(" - Oxígeno   :", res_o)

# ---------- GENERADOR PRINCIPAL ----------
def generador(envios):
    for i in range(5):  # solo 5 datos para prueba inicial
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
    from multiprocessing import set_start_method
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
