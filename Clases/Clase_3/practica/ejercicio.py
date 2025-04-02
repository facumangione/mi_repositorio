import os
import time

def hijo1():
    time.sleep(2)
    print(f"Soy el hijo 1 y mi PID es {os.getpid()}")
    os._exit(0)  

def hijo2():
    time.sleep(3)
    print(f"Soy el hijo 2 y mi PID es {os.getpid()}")
    os._exit(0)

pid1 = os.fork()
if pid1 == 0:
    hijo1()

pid2 = os.fork()
if pid2 == 0:
    hijo2()

# El padre no espera a los hijos
print("Soy el padre y estoy terminando")
os._exit(0)
