import os
import time

pid = os.fork()

if pid == 0:  # Proceso hijo
    time.sleep(5)  # Sigue vivo tras la muerte del padre
    print(f"Hijo {os.getpid()} adoptado por init/systemd")
else:
    print(f"Padre {os.getpid()} finalizado.")
    exit(0)  # Padre termina antes que el hijo
