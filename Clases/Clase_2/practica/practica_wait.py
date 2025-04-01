import os

pid = os.fork()

if pid == 0:  # Proceso hijo
    print(f"Hijo {os.getpid()} en ejecución.")
    exit(0)
else:  # Proceso padre
    print(f"Padre {os.getpid()} esperando al hijo...")
    os.wait()  # Espera a que el hijo termine
    print("El hijo ha terminado.")
