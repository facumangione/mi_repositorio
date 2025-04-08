# Ejercicio 1: Pipeline de procesos

import os

def main():
    # Pipe 1: padre → hijo1
    r1, w1 = os.pipe()
    # Pipe 2: hijo1 → hijo2
    r2, w2 = os.pipe()
    # Pipe 3: hijo2 → padre
    r3, w3 = os.pipe()

    pid1 = os.fork()

    if pid1 == 0:
        # 👶 HIJO 1 - duplica el número
        os.close(w1)
        os.close(r2)
        os.close(r3)
        os.close(w3)

        dato = int(os.read(r1, 1024).decode())
        print(f"[HIJO1] Recibido: {dato}")
        resultado = dato * 2
        print(f"[HIJO1] Enviando: {resultado}")
        os.write(w2, str(resultado).encode())

        os.close(r1)
        os.close(w2)
        os._exit(0)

    else:
        pid2 = os.fork()
        if pid2 == 0:
            # 👶 HIJO 2 - suma 10
            os.close(w1)
            os.close(r1)
            os.close(w2)
            os.close(r3)

            dato = int(os.read(r2, 1024).decode())
            print(f"[HIJO2] Recibido: {dato}")
            resultado = dato + 10
            print(f"[HIJO2] Enviando: {resultado}")
            os.write(w3, str(resultado).encode())

            os.close(r2)
            os.close(w3)
            os._exit(0)

        else:
            # 🧑 PADRE
            os.close(r1)
            os.close(r2)
            os.close(w2)
            os.close(w3)

            numero = 5
            print(f"[PADRE] Enviando número: {numero}")
            os.write(w1, str(numero).encode())
            os.close(w1)

            final = os.read(r3, 1024).decode()
            print(f"[PADRE] Resultado final: {final}")
            os.close(r3)

            os.wait()
            os.wait()

if __name__ == "__main__":
    main()


# Chat simple entre padre e hijo
import os

def main():
    # Pipe A: padre → hijo
    padre_escribe, hijo_lee = os.pipe()
    # Pipe B: hijo → padre
    hijo_escribe, padre_lee = os.pipe()

    pid = os.fork()

    if pid == 0:
        # 👶 HIJO
        os.close(padre_escribe)
        os.close(padre_lee)

        mensaje = os.read(hijo_lee, 1024).decode()
        print(f"[HIJO] Recibido del padre: {mensaje}")

        respuesta = f"Hola padre, recibí tu mensaje: '{mensaje}'"
        os.write(hijo_escribe, respuesta.encode())

        os.close(hijo_lee)
        os.close(hijo_escribe)
        os._exit(0)

    else:
        # 🧑 PADRE
        os.close(hijo_lee)
        os.close(hijo_escribe)

        mensaje = "Hola hijo, ¿cómo estás?"
        os.write(padre_escribe, mensaje.encode())

        respuesta = os.read(padre_lee, 1024).decode()
        print(f"[PADRE] Respuesta del hijo: {respuesta}")

        os.close(padre_escribe)
        os.close(padre_lee)

        os.wait()

if __name__ == "__main__":
    main()
