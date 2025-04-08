# Ejercicio teorico "Un proceso padre envía un mensaje al hijo usando un pipe."
import os

def main():
    # 1. Crear el pipe
    r_fd, w_fd = os.pipe()

    # 2. Crear proceso hijo
    pid = os.fork()

    if pid > 0:
        # 🧑‍🦰 Proceso padre
        os.close(r_fd)  # No va a leer, entonces cierra el extremo de lectura

        mensaje = "Hola desde el padre"
        os.write(w_fd, mensaje.encode())  # Escribe mensaje en el pipe
        os.close(w_fd)  # Cierra después de escribir

        os.wait()  # Espera que el hijo termine

    else:
        # 👶 Proceso hijo
        os.close(w_fd)  # No va a escribir, entonces cierra el extremo de escritura

        recibido = os.read(r_fd, 1024)  # Lee del pipe
        print(f"[HIJO] Mensaje recibido: {recibido.decode()}")
        os.close(r_fd)  # Cierra después de leer

if __name__ == "__main__":
    main()

# [HIJO] Mensaje recibido: Hola desde el padre



# Ejercicio teorico 2 "pipeline simple"
import os

def main():
    r_fd, w_fd = os.pipe()  # Creamos el pipe

    pid = os.fork()

    if pid > 0:
        # 🧑 Padre: envía mensaje
        os.close(r_fd)  # No va a leer

        mensaje = "hola mundo desde pipes"
        os.write(w_fd, mensaje.encode())
        os.close(w_fd)

        os.wait()

    else:
        # 👶 Hijo: transforma mensaje
        os.close(w_fd)  # No va a escribir

        datos = os.read(r_fd, 1024).decode()
        print(f"[HIJO] Mensaje transformado: {datos.upper()}")
        os.close(r_fd)

if __name__ == "__main__":
    main()

# [HIJO] Mensaje transformado: HOLA MUNDO DESDE PIPES


# Ejercicio teorico 3 "comunicación padre ↔ hijo"

import os

def main():
    # Creamos dos pipes: uno para cada dirección
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid > 0:
        # 🧑 PADRE
        os.close(padre_a_hijo_r)  # Cierra lectura hacia hijo
        os.close(hijo_a_padre_w)  # Cierra escritura desde hijo

        numero = 21
        print(f"[PADRE] Enviando número: {numero}")
        os.write(padre_a_hijo_w, str(numero).encode())
        os.close(padre_a_hijo_w)

        # Recibe respuesta del hijo
        resultado = os.read(hijo_a_padre_r, 1024).decode()
        print(f"[PADRE] Hijo devolvió: {resultado}")
        os.close(hijo_a_padre_r)

        os.wait()

    else:
        # 👶 HIJO
        os.close(padre_a_hijo_w)  # Cierra escritura desde padre
        os.close(hijo_a_padre_r)  # Cierra lectura hacia padre

        dato = os.read(padre_a_hijo_r, 1024).decode()
        print(f"[HIJO] Recibí del padre: {dato}")

        doble = int(dato) * 2
        os.write(hijo_a_padre_w, str(doble).encode())
        os.close(hijo_a_padre_w)
        os.close(padre_a_hijo_r)

if __name__ == "__main__":
    main()

# [PADRE] Enviando número: 21  
# [HIJO] Recibí del padre: 21  
# [PADRE] Hijo devolvió: 42


