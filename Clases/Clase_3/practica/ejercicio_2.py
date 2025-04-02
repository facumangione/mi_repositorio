import os

def crear_hijo(nivel, max_nivel):
    if nivel > max_nivel:
        return
    
    pid = os.fork()
    
    if pid == 0:  # Proceso hijo
        print(f"[HIJO {nivel}] Soy el hijo y mi PID es {os.getpid()}, el de mi padre es {os.getppid()}")
        crear_hijo(nivel + 1, max_nivel)  # El hijo genera otro hijo
    else:  # Proceso padre
        os.wait()  # Solo el padre espera a su hijo antes de terminar

if __name__ == "__main__":
    print(f"[PADRE] PID inicial: {os.getpid()}")
    crear_hijo(1, 5)  # Crear 5 hijos en cascada
