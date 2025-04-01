import os

pid = os.fork()

if pid == 0:  # Código del proceso hijo
    print("Soy el hijo, ahora ejecutaré ls...")
    os.execlp("ls", "ls", "-l")  # Reemplaza el proceso con "ls -l"
else:
    os.wait()  # El padre espera a que el hijo termine
    print("Soy el padre y mi hijo terminó.")
