🧩 Ejercicio 1:

    Crear un sistema donde:

        El productor genera números del 1 al 10.

        El filtro solo deja pasar los pares.

        El consumidor los imprime.

from multiprocessing import Process, Queue

def productor(q):
    for i in range(1, 11):
        print(f'[Productor] Enviando: {i}')
        q.put(i)
    q.put('FIN')

def filtro(entrada, salida):
    while True:
        dato = entrada.get()
        if dato == 'FIN':
            salida.put('FIN')
            break
        if dato % 2 == 0:
            print(f'[Filtro] Pasando par: {dato}')
            salida.put(dato)

def consumidor(q):
    while True:
        dato = q.get()
        if dato == 'FIN':
            print('[Consumidor] Fin de datos.')
            break
        print(f'[Consumidor] Recibido: {dato}')

if __name__ == '__main__':
    q1 = Queue()
    q2 = Queue()

    p1 = Process(target=productor, args=(q1,))
    p2 = Process(target=filtro, args=(q1, q2))
    p3 = Process(target=consumidor, args=(q2,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

🧩 Ejercicio 2:

    Extender lo anterior con múltiples filtros: uno para pares, otro para mayores que 5.

def filtro_pares(entrada, salida):
    while True:
        dato = entrada.get()
        if dato == 'FIN':
            salida.put('FIN')
            break
        if dato % 2 == 0:
            print(f'[Filtro Pares] Pasando: {dato}')
            salida.put(dato)

def filtro_mayores_que_5(entrada, salida):
    while True:
        dato = entrada.get()
        if dato == 'FIN':
            salida.put('FIN')
            break
        if dato > 5:
            print(f'[Filtro >5] Pasando: {dato}')
            salida.put(dato)

if __name__ == '__main__':
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()

    p1 = Process(target=productor, args=(q1,))
    p2 = Process(target=filtro_pares, args=(q1, q2))
    p3 = Process(target=filtro_mayores_que_5, args=(q2, q3))
    p4 = Process(target=consumidor, args=(q3,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

🧾 RESUMEN GENERAL DE LO APRENDIDO
🟦 1. Concepto de Queue

    Estructura FIFO: los datos salen en el mismo orden en que entran.

    Evita condiciones de carrera.

    Utilizada en sistemas operativos para planificación y comunicación entre procesos/hilos.

🟦 2. Implementación Interna y Ciclo de Vida

    Internamente usa buffers y locks.

    Ciclo: creación → envío (put) → recepción (get) → finalización.

    Puede usarse de forma limitada (bounded) para forzar sincronización.

🟦 3. Implementación en Python

    Usamos multiprocessing.Queue.

    Métodos clave: put() para enviar, get() para recibir.

    Cada proceso trabaja de forma segura sin necesidad de locks adicionales.

🟦 4. Comunicación Unidireccional

    Un proceso envía, otro recibe.

    Ideal para cadenas de procesamiento (pipeline).

    Se usan mensajes especiales como 'FIN' para indicar el fin de datos.

🟦 5. Ejercicios Prácticos

    Ejercicio 1: pasar solo los números pares.

    Ejercicio 2: aplicar múltiples filtros: pares y mayores que 5.

🟦 6. Prevención de Problemas Comunes

    Evitar deadlocks con mensajes de control y timeout en get().

    Usar queues con tamaño limitado para no saturar procesos.

🟦 7. Diferencias con Pipes
Queue	Pipe
Más simple de usar	Requiere manejar extremos
Segura entre procesos	Limitada y menos flexible
Bidireccional opcional	Unidireccional por defecto
✅ Para cerrar

Te recomiendo ahora:

    Ejecutar y probar los dos ejemplos.

    Comentar el código como práctica de documentación.

    Mostrar al profesor al menos uno de ellos funcionando.

    Volver a repasar los conceptos antes de avanzar a cosas como sockets o programación asíncrona.