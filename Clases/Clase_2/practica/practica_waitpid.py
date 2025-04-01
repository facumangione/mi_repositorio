import os

pid = os.fork()

if pid == 0:
    print(f"Hijo {os.getpid()} trabajando...")
    exit(0)
else:
    print(f"Padre {os.getpid()} esperando a {pid}...")
    os.waitpid(pid, 0)  # Espera específicamente al hijo `pid`
    print(f"Hijo {pid} finalizado.")
