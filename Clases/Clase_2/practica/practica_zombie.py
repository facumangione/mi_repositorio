import os
import time

pid = os.fork()

if pid == 0:  # Proceso hijo
    print(f"Hijo {os.getpid()} terminado.")
    exit(0)  # Termina inmediatamente
else:  # Proceso padre
    print(f"Padre {os.getpid()} sin hacer wait()")
    time.sleep(10)  # No recoge al hijo
    os.system(f"ps -o pid,ppid,state,command | grep {pid}")  # Verifica estado
