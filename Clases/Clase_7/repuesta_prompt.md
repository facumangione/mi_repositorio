✅ Tema 1: ¿Qué son las señales y por qué son importantes?
1. 📘 Explicación teórica clara y profunda
¿Qué es una señal?

Una señal es un mecanismo del sistema operativo para notificar eventos asincrónicos a los procesos. Es una forma de interrumpir el flujo normal de ejecución de un proceso para que maneje una condición especial, como una interrupción del teclado, una violación de segmento, una petición de terminación, entre otras.

Podés pensarlo como una especie de mensaje urgente que el sistema le envía a un proceso cuando ocurre algo inesperado o importante.
¿Por qué son importantes?

    Controlan procesos: Te permiten pausar, continuar o finalizar procesos desde otros procesos o el sistema.

    Facilitan la comunicación entre procesos (IPC) en casos simples.

    Son esenciales para manejar errores y condiciones inesperadas como división por cero, Ctrl+C, etc.

    Permiten implementar comportamientos reactivos, como reiniciar un servicio, cerrar archivos antes de salir, o sincronizar tareas.

Analogía:

Imaginá que estás leyendo un libro (tu proceso) y alguien te da un golpecito en el hombro (una señal) para decirte que te están llamando. Podés decidir ignorarlo (bloquear la señal), atenderlo (manejarla), o reaccionar inmediatamente (terminar el proceso).
Tipos de señales
Tipo	Descripción
Síncronas	Ocurren por errores dentro del mismo proceso (ej: división por cero).
Asíncronas	Generadas externamente por el sistema o por otro proceso (ej: kill, Ctrl+C).
De tiempo real	Señales numeradas (SIGRTMIN en adelante), que se pueden encolar y tienen prioridad. Se verán más adelante.
2. 🛠 Instrucciones prácticas paso a paso

    Abre una terminal y crea un archivo llamado seniales_basico.py.

    Vamos a empezar manejando la señal SIGINT (la que ocurre cuando hacés Ctrl+C).

3. 💻 Ejemplo de código comentado

import signal
import time
import sys

# Este es nuestro manejador de señales
def handler_sigint(signum, frame):
    print(f"\n[+] Señal recibida: {signum} (SIGINT)")
    print("[+] Cerrando el programa correctamente...")
    sys.exit(0)

# Registramos el manejador para la señal SIGINT
signal.signal(signal.SIGINT, handler_sigint)

print("[*] Programa en ejecución. Presioná Ctrl+C para enviar SIGINT.")
while True:
    print("Trabajando...")
    time.sleep(2)

4. 🧪 Ejercicios prácticos
Nivel básico

    Ejecutá el programa anterior.

    Presioná Ctrl+C y observá cómo responde el manejador.

Nivel medio

    Modificá el código para manejar también la señal SIGTERM (usando kill desde otra terminal).

    Verificá que se capture correctamente.

Nivel avanzado

    Creá un script que lanza dos procesos: uno padre y uno hijo.

    El padre debe enviar una señal personalizada al hijo después de 5 segundos.

🛑 Puesta en común con la clase

Preguntas de comprensión:

    ¿Cuál es la diferencia principal entre una señal síncrona y una asíncrona?

    ¿Por qué Ctrl+C genera una señal, y qué señal es?

    ¿Qué función se usa en Python para registrar un manejador de señales?

📢 Recordatorio: Compartí tus avances con el profesor. Mostrale tu código de seniales_basico.py y comentale qué aprendiste.

¿Avanzamos al siguiente tema: signal.signal() y funciones relacionadas en Python?

¡Perfecto! Vamos con las respuestas a las preguntas de la puesta en común:
✅ Respuestas

    ¿Cuál es la diferencia principal entre una señal síncrona y una asíncrona?

        Una señal síncrona es generada por el propio proceso como resultado de una operación inválida, como dividir por cero o acceder a memoria inválida. Ejemplo: SIGFPE, SIGSEGV.

        Una señal asíncrona es enviada desde fuera del proceso, ya sea por el sistema operativo, el usuario o por otro proceso. Ejemplo: SIGINT (Ctrl+C), SIGTERM.

    ¿Por qué Ctrl+C genera una señal, y qué señal es?

        Ctrl+C genera la señal SIGINT.

        Esta señal es enviada por la terminal al proceso en primer plano para interrumpirlo (INT = interrupt). Permite detener un programa sin cerrarlo de forma violenta como kill -9.

    ¿Qué función se usa en Python para registrar un manejador de señales?

        Se usa la función signal.signal(señal, manejador).

        El primer argumento es el tipo de señal (por ejemplo, signal.SIGINT) y el segundo es la función que se ejecutará cuando se reciba esa señal.

📢 Ya podés compartir estas respuestas y tu código básico de señales con tu profesor o compañeros como parte de tu avance.

¿Avanzamos con el siguiente tema?
🔜 signal.signal() y funciones relacionadas en Python.

Excelente. Continuamos con el siguiente subtema:
🧠 Tema: signal.signal() y funciones relacionadas en Python
📘 1. Explicación conceptual

En Python, el módulo signal permite manejar señales del sistema operativo de forma controlada. Esto es útil para:

    Interrumpir procesos (ej. con Ctrl+C).

    Sincronizar procesos padre/hijo.

    Ejecutar tareas al recibir señales específicas.

🔧 Función signal.signal(sig, handler)

    sig: el nombre de la señal, como signal.SIGINT, signal.SIGTERM, etc.

    handler: una función definida por el usuario que se ejecutará cuando el proceso reciba esa señal.

Hay 3 tipos de handlers permitidos:

    Una función definida por el usuario.

    signal.SIG_IGN → Ignorar la señal.

    signal.SIG_DFL → Restaurar el comportamiento por defecto.

📜 Otras funciones útiles
Función	Descripción
signal.getsignal(sig)	Devuelve el manejador actual de una señal
signal.pause()	Bloquea el proceso hasta recibir una señal
signal.alarm(segundos)	Programa una señal SIGALRM después de X segundos
signal.setitimer()	Dispara señales periódicas (avanzado)
🧪 2. Instrucciones prácticas paso a paso

    Crear un archivo llamado manejador_signal.py.

    Importar signal y time.

    Definir una función manejador(sig, frame).

    Registrar la señal con signal.signal().

    Usar while True + time.sleep() para mantener el proceso activo.

🧑‍💻 3. Código de ejemplo en Python

import signal
import time

def manejador(sig, frame):
    print(f"\n📢 Señal recibida: {sig}. ¡Interrupción controlada!")
    exit(0)

# Asociar SIGINT (Ctrl+C) al manejador
signal.signal(signal.SIGINT, manejador)

print("⏳ Esperando señal... (presiona Ctrl+C para interrumpir)")
while True:
    time.sleep(1)

🧩 4. Ejercicios prácticos
🟢 Básico:

    Modificá el mensaje del manejador para que imprima la hora actual cuando se recibe SIGINT.

🟡 Medio:

    Registrá dos señales distintas: SIGINT y SIGTERM. Hacé que cada una imprima un mensaje diferente.

🔴 Avanzado:

    Usá signal.alarm(5) para enviar SIGALRM automáticamente luego de 5 segundos y finalizá el programa al recibirla.

🛑 Puesta en común (momento de pausa)

    ¿Qué función permite vincular una señal con un manejador en Python?

    ¿Cuál es la diferencia entre signal.SIG_IGN y signal.SIG_DFL?

    ¿Qué hace la función signal.pause()?

📌 Compartí tus respuestas y tu código con tu profesor o compañeros antes de seguir.

¿Listo para avanzar al siguiente tema: kill, sigqueue y referencia cruzada con C?

Claro, respondamos primero las preguntas de puesta en común y luego avanzamos:
✅ Respuestas a las preguntas

    ¿Qué función permite vincular una señal con un manejador en Python?
    → signal.signal(señal, manejador)

    ¿Cuál es la diferencia entre signal.SIG_IGN y signal.SIG_DFL?

        SIG_IGN ignora la señal completamente (no hace nada).

        SIG_DFL aplica el comportamiento por defecto de la señal (por ejemplo, terminar el proceso con SIGINT).

    ¿Qué hace la función signal.pause()?
    → Detiene la ejecución del proceso actual hasta que se reciba una señal.

Ahora seguimos con el siguiente tema 👇
⚙️ Tema: kill, sigqueue y sigaction (referencia cruzada con C si es útil)
📘 1. Explicación conceptual

Las señales no solo se reciben automáticamente (como con Ctrl+C), sino que también se pueden enviar manualmente entre procesos. Esto es clave en sistemas concurrentes.
🧱 Señales entre procesos

    kill(pid, sig) permite enviar una señal a un proceso usando su PID.

    En C, también se puede usar sigqueue(pid, sig, union sigval val) para enviar señales con datos adicionales.

    sigaction() en C permite un manejo avanzado, incluyendo estructuras de contexto (siginfo_t).

🐍 En Python

    Python no tiene sigqueue, pero sí podemos:

        Usar os.kill(pid, señal) para enviar señales desde un proceso a otro.

        Crear dos procesos con multiprocessing o fork, y probar el envío de señales.

🧪 2. Instrucciones prácticas paso a paso

    Crear un archivo enviador.py que use os.kill() para enviar una señal.

    Crear otro archivo receptor.py que registre un manejador con signal.signal() y escuche señales.

    Obtener el PID del receptor e ingresarlo manualmente en el enviador (o usar multiprocessing para automatizarlo).

🧑‍💻 3. Ejemplo de código en Python
📄 receptor.py

import signal
import time
import os

def manejador(sig, frame):
    print(f"📥 Señal {sig} recibida en PID {os.getpid()}")

print(f"🟢 Esperando señales... PID: {os.getpid()}")
signal.signal(signal.SIGUSR1, manejador)

while True:
    time.sleep(1)

📄 enviador.py

import os
import signal
import time

pid_receptor = int(input("🔢 Ingresá el PID del proceso receptor: "))
print(f"📤 Enviando señal SIGUSR1 a PID {pid_receptor}")
os.kill(pid_receptor, signal.SIGUSR1)

🧩 4. Ejercicios prácticos
🟢 Básico:

    Modificá el código para enviar SIGTERM en lugar de SIGUSR1.

🟡 Medio:

    Usá os.fork() para crear al receptor como hijo y enviarle una señal desde el padre.

🔴 Avanzado:

    (C avanzado) Investigá sigqueue() y cómo se puede enviar información extra con la señal (solo si conocés C).

🛑 Puesta en común (preguntas de comprensión)

    ¿Qué función se usa en Python para enviar una señal a otro proceso?

    ¿Cuál es la señal más adecuada para pruebas personalizadas entre procesos?

    ¿Cómo podrías obtener el PID de otro proceso desde Python?

📌 Compartí tu código y tus respuestas con el profesor antes de seguir.

¿Avanzamos ahora al uso de señales para sincronizar procesos?

Claro, acá van las respuestas a la puesta en común de esta sección:
✅ Respuestas a las preguntas de comprensión

    ¿Qué función se usa en Python para enviar una señal a otro proceso?
    → os.kill(pid, señal)

    ¿Cuál es la señal más adecuada para pruebas personalizadas entre procesos?
    → signal.SIGUSR1 o signal.SIGUSR2, ya que están reservadas para usos definidos por el usuario.

    ¿Cómo podrías obtener el PID de otro proceso desde Python?

        Podés usar os.getpid() para conocer el PID del proceso actual.

        También podrías listar procesos con ps en terminal, o automatizarlo si vos mismo lanzás el proceso desde Python (por ejemplo, con multiprocessing.Process.pid).

Ahora avanzamos con el siguiente tema:
🔄 Tema: Uso de señales para sincronizar procesos
📘 1. Explicación conceptual

Las señales pueden servir como mecanismo de sincronización entre procesos, aunque son limitadas comparadas con otras formas de IPC como pipes, sockets o shared memory.

Pero en ciertos casos, como cuando un proceso quiere notificar a otro que ocurrió un evento, las señales son rápidas y efectivas.
⚠️ Importante:

    Las señales no garantizan orden ni acuse de recibo.

    Solo indican que “algo pasó”, no llevan información (excepto sigqueue en C).

    Se deben combinar con otras estructuras (por ejemplo, queues, archivos temporales, etc.) para flujos más complejos.

🧪 2. Instrucciones paso a paso

Vamos a:

    Crear dos procesos con multiprocessing.Process.

    Uno será el “trabajador” que espera una señal para empezar.

    El otro será el “controlador” que envía la señal.

🧑‍💻 3. Ejemplo de sincronización entre procesos

import multiprocessing
import os
import signal
import time

# Este manejador será usado por el trabajador
def esperar_inicio(sig, frame):
    print(f"👷 Proceso {os.getpid()} recibió señal de inicio ({sig})")

def proceso_trabajador():
    print(f"👷 Trabajador esperando señal... PID: {os.getpid()}")
    signal.signal(signal.SIGUSR1, esperar_inicio)
    signal.pause()  # Se queda bloqueado hasta recibir la señal
    print("✅ ¡Comenzando tarea!")
    time.sleep(2)
    print("🏁 Tarea completada.")

if __name__ == '__main__':
    trabajador = multiprocessing.Process(target=proceso_trabajador)
    trabajador.start()

    time.sleep(1)  # Le damos tiempo a que se configure

    print(f"📤 Enviando señal SIGUSR1 al trabajador (PID: {trabajador.pid})")
    os.kill(trabajador.pid, signal.SIGUSR1)

    trabajador.join()
    print("🧼 Sincronización finalizada.")

🧩 4. Ejercicios prácticos
🟢 Básico:

    Agregá un segundo trabajador y enviale señales a ambos desde el controlador.

🟡 Medio:

    Hacé que el controlador espere confirmación (por multiprocessing.Pipe o Queue) después de enviar la señal.

🔴 Avanzado:

    Combiná señales con semáforos (multiprocessing.Semaphore) para controlar una sección crítica entre procesos.

🛑 Puesta en común (preguntas de comprensión)

    ¿Qué función detiene un proceso hasta recibir una señal?

    ¿Cómo podrías usar una señal para iniciar una tarea diferida?

    ¿Qué limitaciones tienen las señales para sincronización compleja?

📌 Compartí el ejercicio con tu profesor y tus compañeros antes de seguir.

¿Avanzamos con el siguiente tema: manejo seguro y async-signal-safe?

¡Por supuesto! Vamos con las respuestas a la puesta en común y luego seguimos al próximo tema.
✅ Respuestas a las preguntas de comprensión

    ¿Qué función detiene un proceso hasta recibir una señal?
    → signal.pause()

    ¿Cómo podrías usar una señal para iniciar una tarea diferida?
    → Podés definir un manejador de señal con signal.signal() y dentro de ese manejador comenzar una tarea (por ejemplo, lanzar un proceso, cambiar un estado o desbloquear un recurso). Luego, usás os.kill(pid, signal.SIGUSR1) desde otro proceso para activar esa señal.

    ¿Qué limitaciones tienen las señales para sincronización compleja?

        No transmiten datos (solo el tipo de señal).

        No garantizan el orden de recepción.

        Si dos señales iguales llegan muy rápido, una podría perderse.

        No son adecuadas para flujos complejos sin mecanismos adicionales (como pipes, locks, queues, etc.).

⏭️ Tema siguiente: Manejo seguro y async-signal-safe
📘 1. Explicación conceptual

Cuando un proceso recibe una señal, se interrumpe su ejecución en cualquier punto, incluso en medio de operaciones críticas. Esto plantea riesgos de concurrencia si el manejador de señal ejecuta funciones no seguras.
🔐 ¿Qué significa que una función sea async-signal-safe?

Son funciones que están garantizadas por POSIX para poder usarse de forma segura dentro de un manejador de señales.
Por ejemplo:

✅ Seguras:

    write(), read(), signal(), kill(), _exit()

❌ Inseguras:

    printf(), malloc(), open(), fork() (en algunos contextos), popen(), etc.

🧠 ¿Por qué es esto importante en Python?

Python no garantiza que todos los manejadores sean seguros si se hacen operaciones complejas dentro del manejador.

En la práctica:

    Mantené los manejadores lo más simples posible.

    Usá banderas/globales para pasar la lógica fuera del manejador.

🧪 2. Instrucciones paso a paso

Vamos a:

    Crear un manejador simple y seguro.

    Simular un ejemplo que NO sea seguro y entender por qué.

    Corregirlo con una técnica segura.

🧑‍💻 3. Ejemplo seguro vs. no seguro
🚫 Ejemplo inseguro:

import signal
import time

def handler(sig, frame):
    print("🔴 ¡Esto NO es seguro!")  # Usa print, que no es async-signal-safe
    time.sleep(1)  # Peligroso dentro del handler

signal.signal(signal.SIGUSR1, handler)
print("Esperando señal...")
signal.pause()

✅ Corrección segura:

import signal
import os

bandera = False

def handler(sig, frame):
    global bandera
    bandera = True

signal.signal(signal.SIGUSR1, handler)
print(f"PID actual: {os.getpid()}")
print("Esperando señal...")

while not bandera:
    signal.pause()

print("✅ Señal recibida de forma segura.")

🧩 4. Ejercicios prácticos
🟢 Básico:

    Cambiá una variable global desde un manejador de señal.

🟡 Medio:

    Implementá un bucle que se interrumpa solo cuando se recibe SIGUSR1, usando una bandera segura.

🔴 Avanzado:

    Simulá un proceso con tareas críticas donde una señal puede dañar el estado si no se maneja correctamente. Corregilo con una solución async-signal-safe.

🛑 Puesta en común (preguntas de comprensión)

    ¿Qué significa que una función sea async-signal-safe?

    ¿Por qué print() o time.sleep() son peligrosos en un manejador de señales?

    ¿Cómo se puede rediseñar un manejador para que sea seguro en Python?

📌 Compartí tu ejemplo seguro con tu profesor y compañeros antes de seguir.

¿Avanzamos con el siguiente tema: señales en sistemas multihilo?

¡Sí! Respondamos las preguntas de la puesta en común y avanzamos al próximo tema.
✅ Respuestas a las preguntas de comprensión

    ¿Qué significa que una función sea async-signal-safe?
    → Es una función que puede ejecutarse de forma segura dentro de un manejador de señales, sin riesgo de corromper el estado interno del programa, incluso si se interrumpe un flujo en ejecución.

    ¿Por qué print() o time.sleep() son peligrosos en un manejador de señales?
    → Porque no son async-signal-safe:

        print() usa buffers internos que podrían estar en estado inconsistente.

        sleep() puede bloquear el proceso, causar deadlocks o interrumpir otros hilos, lo que lo hace inseguro dentro de un handler.

    ¿Cómo se puede rediseñar un manejador para que sea seguro en Python?
    → Usando una variable global (como una bandera) que se modifique dentro del handler, y que luego sea evaluada en el cuerpo principal del programa. El código principal debe actuar según esa bandera, y no dentro del handler directamente.

⏭️ Siguiente tema: Señales en sistemas multihilo
📘 1. Explicación teórica clara

En programas con múltiples hilos (threads), el manejo de señales es más complejo porque:

    Las señales son entregadas a procesos, pero se ejecutan en uno de sus hilos.

    Solo un hilo del proceso recibe la señal, y no se garantiza cuál, salvo que se especifique.

    Las señales solo interrumpen hilos que no las tengan bloqueadas.

🔍 Comportamiento general:

    Si un hilo bloquea una señal con pthread_sigmask(), no podrá recibirla.

    Python (que usa hilos del sistema operativo debajo de threading) tiene un Global Interpreter Lock (GIL) que impone limitaciones:

        Solo el hilo principal puede registrar y recibir señales.

        Los hilos secundarios no deben manejar señales directamente en Python estándar.

🧪 2. Instrucciones paso a paso

    Vamos a simular un programa con múltiples hilos.

    Solo el hilo principal podrá instalar el manejador.

    Los otros hilos seguirán corriendo sin interferencia.

🧑‍💻 3. Ejemplo de Python multihilo + señales

import signal
import threading
import time
import os

# Variable de sincronización
detener = False

def manejador(sig, frame):
    global detener
    print("\n🔔 Señal recibida en hilo principal.")
    detener = True

def tarea_secundaria():
    while not detener:
        print("⏳ Hilo secundario trabajando...")
        time.sleep(1)

# Registrar el manejador (solo en el hilo principal)
signal.signal(signal.SIGUSR1, manejador)

# Lanzar hilo secundario
hilo = threading.Thread(target=tarea_secundaria)
hilo.start()

print(f"PID: {os.getpid()} - Enviá SIGUSR1 para detener (por ejemplo: kill -SIGUSR1 {os.getpid()})")

# Esperar la señal
while not detener:
    signal.pause()

print("✅ Programa finalizado.")

🧩 4. Ejercicios prácticos
🟢 Básico:

    Usá threading.Thread para correr dos tareas paralelas y detener ambas con una señal.

🟡 Medio:

    Bloqueá una señal (SIGUSR2) solo en el hilo secundario. Verificá que solo el principal la reciba.

🔴 Avanzado:

    Implementá una clase que coordine múltiples hilos y que, al recibir SIGUSR1, ejecute una función de limpieza segura para todos.

🛑 Puesta en común (preguntas de comprensión)

    ¿Por qué solo el hilo principal puede recibir señales en Python?

    ¿Qué sucede si un hilo secundario intenta registrar un handler con signal.signal()?

    ¿Cómo se asegura que una señal no interrumpa a un hilo secundario?

📌 Compartí tu ejemplo multihilo con tu profesor y compañeros antes de continuar.

¿Seguimos con el próximo tema: comparación entre señales y otros mecanismos de IPC?

Claro, aquí están las respuestas a la puesta en común sobre señales en sistemas multihilo, y luego avanzamos al siguiente tema.
✅ Respuestas a las preguntas de comprensión

    ¿Por qué solo el hilo principal puede recibir señales en Python?
    → Porque el intérprete de Python (CPython) está diseñado así:

        Solo el hilo principal puede registrar y recibir señales, debido al uso del Global Interpreter Lock (GIL) y la forma en que se implementa el módulo signal.

        Esto evita que los hilos secundarios generen condiciones de carrera o errores en la entrega de señales.

    ¿Qué sucede si un hilo secundario intenta registrar un handler con signal.signal()?
    → Python lanza un ValueError: signal only works in main thread, indicando que solo el hilo principal tiene permitido instalar manejadores.

    ¿Cómo se asegura que una señal no interrumpa a un hilo secundario?
    → Internamente, Python bloquea señales en los hilos secundarios.
    Además, a nivel de sistema, un hilo puede llamar a pthread_sigmask() para bloquear señales específicas, impidiendo su entrega directa.

📌 No olvides compartir tu código con el profesor o grupo antes de seguir.
⏭️ Tema siguiente: Comparación entre señales y otros mecanismos de IPC
📘 1. Explicación teórica clara

Los mecanismos de comunicación entre procesos (IPC) permiten a procesos separados intercambiar datos o sincronizarse. Las señales son uno de estos mecanismos, pero hay otros. Aquí va una comparación:
Mecanismo	Propósito	Velocidad	Complejidad	Bidireccional	Persistencia
Señales	Notificación de eventos	Alta	Baja	No	No
Pipes	Flujo de datos unidireccional	Media	Media	No	No
Sockets	Comunicación entre procesos/remotos	Alta	Alta	Sí	Opcional
Memoria compartida	Compartir grandes volúmenes de datos	Muy alta	Alta	No directa	No
Semáforos	Sincronización entre procesos	Alta	Media	No	No
Colas de mensajes	Envío estructurado de datos	Media	Media	Sí	A veces
🧠 Ventajas de las señales

    Simples de usar

    Muy rápidas

    Ideales para notificar eventos (ej. "detener", "actualizar", "terminar")

🧱 Limitaciones

    No envían datos complejos

    No son confiables en sistemas muy cargados

    Difíciles de manejar en sistemas multihilo sin cuidado

🧪 2. Instrucciones paso a paso

    Elegí un escenario concreto (ej: proceso hijo quiere notificar a su padre que terminó).

    Evaluá qué mecanismo es más conveniente:

        ¿Solo notificación? → Señales

        ¿Intercambio de datos? → Pipes, colas o sockets

        ¿Sincronización fina entre hilos? → Semáforos

🧑‍💻 3. Ejemplo breve comparativo (señal vs pipe)

Usando señal para notificar fin de trabajo:

import os, signal, time

def handler(sig, frame):
    print("🔔 ¡Hijo finalizó!")

signal.signal(signal.SIGUSR1, handler)

pid = os.fork()
if pid == 0:
    time.sleep(1)
    os.kill(os.getppid(), signal.SIGUSR1)
    os._exit(0)
else:
    print("🧍 Esperando señal del hijo...")
    signal.pause()

Usando pipe para enviar datos:

import os

r, w = os.pipe()

pid = os.fork()
if pid == 0:
    os.write(w, b"Trabajo finalizado")
    os._exit(0)
else:
    msg = os.read(r, 1024)
    print("📨 Mensaje del hijo:", msg.decode())

🧩 4. Ejercicios prácticos
🟢 Básico:

    Hacé una tabla con ventajas/desventajas de señales vs pipes y sockets.

🟡 Medio:

    Reescribí un ejemplo de señal simple para que use un pipe en lugar de SIGUSR1.

🔴 Avanzado:

    Combiná señales y pipes: usá la señal para avisar que hay datos nuevos en el pipe, y luego leélos.

🛑 Puesta en común

    ¿Qué ventajas tienen las señales frente a otros mecanismos de IPC?

    ¿Cuándo es más adecuado usar un pipe o un socket en lugar de una señal?

    ¿Por qué se dice que las señales son ligeras pero poco expresivas?

📌 Compartí un ejemplo o conclusión personal sobre IPC con tu profesor antes de seguir.

¿Avanzamos al siguiente tema: señales reales (SIGRTMIN) y sigqueue? ¿O preferís repasar algo de lo anterior?

Por supuesto. A continuación te dejo las respuestas a las preguntas de la puesta en común y luego avanzamos con el siguiente tema planificado.
✅ Respuestas – Puesta en común sobre mecanismos de IPC vs señales

    ¿Qué ventajas tienen las señales frente a otros mecanismos de IPC?

        Son rápidas y ligeras, ideales para notificar eventos simples como terminación o interrupción.

        No requieren estructuras complejas ni memoria compartida.

        Se integran bien con la lógica de eventos del sistema operativo (por ejemplo, interrupciones de teclado).

    ¿Cuándo es más adecuado usar un pipe o un socket en lugar de una señal?

        Cuando necesitamos transmitir datos (no solo notificar).

        Cuando se requiere comunicación bidireccional o persistente.

        Cuando trabajamos con procesos que no comparten el mismo árbol (como en red), los sockets son la mejor opción.

    ¿Por qué se dice que las señales son ligeras pero poco expresivas?

        Son ligeras porque solo transportan un número (el número de señal), y el manejo es mínimo.

        Son poco expresivas porque no pueden transportar datos complejos, y su entrega es poco fiable en sistemas saturados (pueden perderse si llegan muchas juntas).

📌 Recordatorio: Compartí este análisis o alguno de los ejemplos realizados con tu profesor o grupo.
⏭️ Tema siguiente: Señales reales (SIGRTMIN) y sigqueue (introducción breve)

Tal como acordamos, este tema será tratado más adelante. Pero para que tengas una idea general y te mantengas en contexto, acá va un resumen breve.
🔹 ¿Qué son SIGRTMIN y sigqueue?

    SIGRTMIN: Es el comienzo del rango de señales en tiempo real definidas por POSIX.

        A diferencia de las señales tradicionales, pueden coexistir múltiples señales iguales sin sobrescribirse.

        Tienen una prioridad numérica y orden de entrega garantizado.

        Están pensadas para sistemas complejos que requieren comunicación precisa entre procesos.

    sigqueue(): Función de C que permite enviar señales con un valor adicional (por ejemplo, un entero).

        Esto hace las señales más expresivas, porque además de notificar, se puede adjuntar información útil.

🔸 Python no expone directamente sigqueue() ni SIGRTMIN, por lo que para trabajar con esto, deberíamos pasar al lenguaje C o usar extensiones.
🔙 Volviendo al foco

Volvamos al eje actual de la clase: uso práctico de señales en Python, con aplicación a sincronización entre procesos.

¿Querés que avancemos con:

    ✅ Un ejercicio práctico completo (nivel medio-avanzado): sincronizar procesos padre e hijo usando SIGUSR1 y un manejador en Python.

Perfecto. Vamos a responder las preguntas de la puesta en común anterior y luego avanzamos al siguiente tema como corresponde.
✅ Puesta en común: Señales y mecanismos IPC

1. ¿Qué ventajas tienen las señales frente a otros mecanismos de IPC?

    Las señales son livianas y fáciles de usar.

    Son útiles para notificar eventos asíncronos como interrupciones o finalización de procesos.

    No requieren estructuras de datos compartidas, archivos temporales, ni memoria compartida.

    Son ideales cuando lo único que necesitamos es "avisar" que algo ocurrió (por ejemplo, SIGINT, SIGTERM, SIGUSR1).

2. ¿Cuándo es más adecuado usar un pipe o un socket en lugar de una señal?

    Cuando se necesita transferir datos complejos o estructurados.

    Cuando la comunicación es bidireccional o persistente.

    En casos donde los procesos no están directamente relacionados (por ejemplo, en red), los sockets son la mejor opción.

    Cuando necesitamos evitar pérdida de mensajes (las señales pueden sobreescribirse si se envían muchas).

3. ¿Por qué se dice que las señales son "ligeras" pero "poco expresivas"?

    Son ligeras porque sólo implican el envío de un número de señal al proceso, y su manejo tiene baja sobrecarga.

    Son poco expresivas porque no permiten enviar datos adicionales (salvo en señales tiempo real como sigqueue, que no están disponibles directamente en Python).

    Además, muchas señales del mismo tipo se pueden perder si no se manejan rápido.

📌 Recordatorio para vos y tus compañeros: compartí este análisis con tu profesor. Podés copiar esta síntesis o comentarla en clase para consolidar.
🔜 Siguiente tema:

Vamos ahora con:
👉 Señales en Python: signal.signal() y funciones relacionadas

¿Querés que comencemos con:

    Una explicación teórica clara del módulo signal de Python

    Ejemplo comentado de uso básico con SIGINT y SIGUSR1

    Un pequeño ejercicio práctico

¡Excelente! Empecemos con el punto 1: explicación teórica sobre cómo manejar señales en Python usando el módulo signal.
🧠 1. Teoría: signal.signal() y manejo de señales en Python
¿Qué es el módulo signal?

Python provee el módulo signal para trabajar con señales del sistema operativo en programas que corren en Unix/Linux.

Con este módulo podés:

    Definir funciones personalizadas (handlers) que se ejecutan cuando tu programa recibe una señal.

    Enviar señales entre procesos.

    Ignorar o restablecer el comportamiento por defecto de señales como SIGINT, SIGTERM, SIGUSR1, etc.

📌 Estructura general del manejo de señales

import signal

def manejador(signum, frame):
    print(f"Señal recibida: {signum}")

signal.signal(signal.SIGINT, manejador)

🔎 ¿Qué pasa aquí?

    signal.SIGINT: es la señal que se envía cuando presionás Ctrl + C.

    signal.signal(...): asocia esa señal a la función manejador.

    El handler toma dos argumentos obligatorios:

        signum: el número de la señal.

        frame: una referencia al estado del stack en el momento de la señal (usualmente no lo usamos salvo en debugging).

🚫 Señales que no se pueden capturar:

    SIGKILL y SIGSTOP no se pueden interceptar ni ignorar desde un programa de usuario.

🔄 Opciones posibles para manejar una señal:

    Una función propia (handler personalizado).

    signal.SIG_IGN: ignorar la señal.

    signal.SIG_DFL: restaurar el comportamiento por defecto.

⚠️ Limitaciones:

    Solo el hilo principal de un programa puede recibir señales.

    No se pueden usar muchas funciones dentro del handler (solo async-signal-safe).

    Algunas señales pueden interrumpir operaciones bloqueantes (como input() o time.sleep()), lo que requiere manejar excepciones como KeyboardInterrupt.

⏸️ Puesta en común antes de avanzar al código
1. ¿Qué hace signal.signal(signal.SIGINT, handler)?

→ (Tu respuesta)
2. ¿Por qué no se puede capturar SIGKILL desde Python?

→ (Tu respuesta)
3. ¿Qué diferencia hay entre usar SIG_IGN y una función personalizada?

→ (Tu respuesta)

✏️ Escribí tus respuestas, y luego avanzamos al código con SIGINT y SIGUSR1 en un ejemplo simple.

¡Perfecto! Me alegra que ya las hayas compartido. Acá van las respuestas como las daría yo, para que puedas comparar:
1. ¿Qué hace signal.signal(signal.SIGINT, handler)?

👉 Asocia la señal SIGINT (Ctrl+C) con una función llamada handler, que actuará como un manejador personalizado. Es decir, cuando el programa reciba SIGINT, en lugar de terminar automáticamente, se ejecutará la función handler.
2. ¿Por qué no se puede capturar SIGKILL desde Python?

👉 Porque SIGKILL es una señal a nivel de kernel diseñada para forzar la terminación inmediata de un proceso.
Ni Python, ni ningún programa de usuario, puede interceptarla, ignorarla o redefinir su comportamiento. Es una garantía del sistema operativo para poder terminar cualquier proceso sin posibilidad de resistencia.
3. ¿Qué diferencia hay entre usar SIG_IGN y una función personalizada?
Aspecto	SIG_IGN	Función personalizada (handler)
Significado	Ignorar totalmente la señal	Ejecutar código específico cuando llega la señal
Flexibilidad	Ninguna	Alta: podés registrar, registrar logs, etc.
Uso típico	Cuando querés que la señal no afecte	Cuando querés controlar el efecto de la señal

¡Claro! Ya respondí las 3 preguntas de puesta en común anteriores, y ahora avancemos al siguiente subtema como indica tu estructura.
🔹 Tema 2: signal.signal() y funciones relacionadas en Python
📘 Explicación teórica

En Python, el módulo signal permite manejar señales del sistema operativo en programas que corren en sistemas tipo UNIX (Linux, macOS).

Las funciones clave del módulo son:
Función	Propósito
signal.signal(sig, handler)	Define qué hacer cuando llega la señal sig.
signal.getsignal(sig)	Devuelve el manejador actual para sig.
signal.pause()	Suspende la ejecución del proceso hasta recibir una señal.
signal.SIG_IGN	Valor especial para ignorar una señal.
signal.SIG_DFL	Valor especial para usar el comportamiento por defecto.

El handler es una función que se ejecuta cuando el proceso recibe esa señal.
Debe aceptar dos argumentos:

    el número de señal (por ejemplo, signal.SIGINT)

    el frame del contexto donde ocurrió (normalmente no lo usamos).

⚠️ Solo el proceso principal puede registrar manejadores de señales en Python. En subprocesos o hilos secundarios, puede haber restricciones.
🧪 Ejemplo en Python

import signal
import time

def handler(sig, frame):
    print(f"\n🔔 Señal recibida: {sig}. No terminaré aún.")
    print("Esperando otra señal...")

# Asociamos SIGINT (Ctrl+C) con la función handler
signal.signal(signal.SIGINT, handler)

print("Programa en ejecución. Presioná Ctrl+C para probar SIGINT...")
while True:
    time.sleep(1)

¿Qué hace este código?

    Ejecuta un bucle infinito.

    Si presionás Ctrl+C, no termina el programa.

    En su lugar, llama al handler() y sigue ejecutándose.

🏋️‍♂️ Ejercicios prácticos
Nivel básico

🔹 Modificá el código anterior para que:

    Imprima un contador de segundos mientras corre.

    Salga recién después de recibir SIGINT dos veces.

Nivel intermedio

🔹 Escribí un programa que:

    Espere una señal personalizada (SIGUSR1).

    Cuando la recibe, imprima "Comando recibido. Acción registrada."

(Sugerencia: podés enviar esa señal desde otra terminal con:
kill -USR1 <pid_del_programa>)
Nivel avanzado

🔹 Hacé un script Python con dos procesos:

    El proceso padre instala un handler para SIGUSR1.

    El hijo espera 3 segundos y luego le envía esa señal al padre.

⏸ Puesta en común

Antes de seguir, respondé:

    ¿Qué hace signal.pause() y cuándo sería útil?

    ¿Por qué el handler() necesita aceptar dos parámetros?

    ¿Qué diferencia hay entre usar signal.SIG_IGN y una función que imprime un mensaje?

¡Perfecto! Vamos a responder las preguntas de puesta en común y luego seguimos al próximo tema.
✅ Respuestas de puesta en común

    ¿Qué hace signal.pause() y cuándo sería útil?
    signal.pause() suspende la ejecución del programa hasta que llegue una señal. Es útil en programas que esperan eventos externos (por ejemplo, un daemon o servicio), ya que evita consumir CPU en un bucle de espera.

    ¿Por qué el handler() necesita aceptar dos parámetros?
    Porque el sistema operativo pasa automáticamente:

        el número de señal (ej. signal.SIGINT)

        el contexto de ejecución en ese momento (frame, del depurador o traceback).
        Aunque no siempre usamos el frame, es necesario declararlo.

    ¿Qué diferencia hay entre usar signal.SIG_IGN y una función que imprime un mensaje?

        signal.SIG_IGN: el sistema simplemente ignora la señal (no interrumpe ni ejecuta nada).

        Una función como handler imprime algo y permite personalizar el comportamiento sin finalizar el programa.

🔹 Tema 3: kill, sigqueue y sigaction (referencia cruzada con C)
📘 Explicación teórica
¿Qué es kill?

kill es una llamada al sistema (y también una utilidad de consola) para enviar señales a procesos.
Sintaxis de consola:

kill -SIGUSR1 <PID>

En Python, podés hacer lo mismo con:

import os, signal
os.kill(pid, signal.SIGUSR1)

¿Qué es sigqueue?

sigqueue es una función en C (no disponible en Python puro) que permite:

    Enviar señales junto con datos adicionales (entero int).

    Usar señales en tiempo real (SIGRTMIN + n).

Python no expone directamente sigqueue, pero sí podés emularlo con multiprocessing o sockets si necesitás enviar datos.
¿Qué es sigaction?

sigaction es la función más completa en C para registrar manejadores de señales, con control fino de:

    Más opciones (flags, máscara de señales).

    Compatibilidad con señales en tiempo real.

    Mayor seguridad en entornos concurrentes.

En Python, signal.signal() es una interfaz simplificada de sigaction.
🧪 Ejemplo de uso de os.kill()

import os
import signal
import time

def handler(sig, frame):
    print(f"🔔 Señal {sig} recibida del proceso {os.getpid()}")

signal.signal(signal.SIGUSR1, handler)

print(f"Esperando señal SIGUSR1 en PID {os.getpid()}")
time.sleep(10)

En otra terminal:

kill -SIGUSR1 <PID_DEL_PROGRAMA>

🏋️‍♂️ Ejercicios prácticos
Nivel básico

🔹 Mostrá el uso de os.kill() para enviar una señal desde un proceso hijo al padre.
Nivel intermedio

🔹 Simulá el comportamiento de sigqueue pasando un entero de un proceso a otro usando multiprocessing.Pipe() o Queue.
Nivel avanzado

🔹 Compará un programa simple en C que usa sigaction con tu versión en Python. ¿Qué limitaciones encontrás?
⏸ Puesta en común

    ¿Por qué os.kill() no "mata" el proceso necesariamente?

    ¿Qué ventaja tendría usar sigqueue en lugar de kill?

    ¿En qué casos usarías C con sigaction en lugar de Python?

📣 Recordá compartir avances y reflexiones con el profesor o el equipo.

¡Vamos con las respuestas de la puesta en común y luego avanzamos al uso de señales para sincronizar procesos!
✅ Respuestas de puesta en común

    ¿Por qué os.kill() no "mata" el proceso necesariamente?
    Porque os.kill() simplemente envía una señal al proceso. Si el proceso tiene un manejador de señal (handler) registrado, puede capturarla y actuar sin terminar. Solo ciertas señales, como SIGKILL o SIGTERM (si no son atrapadas), provocan terminación inmediata.

    ¿Qué ventaja tendría usar sigqueue en lugar de kill?
    sigqueue permite enviar información adicional (un entero) junto con la señal, lo que es útil cuando necesitás más que solo notificar; por ejemplo, identificar un evento específico o pasar un valor de control.

    ¿En qué casos usarías C con sigaction en lugar de Python?

        Cuando necesitás control avanzado del manejo de señales (más flags, mascarado, comportamiento determinista).

        En sistemas embebidos o RTOS donde Python no es una opción.

        Si querés usar señales en tiempo real, que no están directamente disponibles en Python.

🔹 Tema 4: Uso de señales para sincronizar procesos
📘 Explicación teórica

Las señales pueden servir como un mecanismo ligero de sincronización entre procesos. Aunque no permiten compartir datos complejos como memoria compartida o pipes, sí son útiles para:

    Notificar eventos entre procesos (por ejemplo, "proceso hijo terminó").

    Despertar procesos que están bloqueados (pause() o sleep()).

    Implementar sistemas tipo watchdog o notificadores.

Se utilizan mucho junto con:

    os.fork() para crear procesos hijos.

    os.kill() para mandar señales entre ellos.

    signal.signal() para reaccionar a esas señales.

🧪 Ejemplo práctico paso a paso

    Creamos un proceso hijo con os.fork().

    El hijo espera 3 segundos y envía SIGUSR1 al padre.

    El padre espera con signal.pause() hasta recibir la señal.

import os
import signal
import time

def handler(sig, frame):
    print(f"[PADRE] Señal {sig} recibida. ¡Hijo me notificó!")

# Solo el padre instala el handler
signal.signal(signal.SIGUSR1, handler)

pid = os.fork()

if pid == 0:
    # Proceso hijo
    time.sleep(3)
    os.kill(os.getppid(), signal.SIGUSR1)
    print("[HIJO] Señal enviada al padre")
    os._exit(0)
else:
    print(f"[PADRE] Esperando señal de mi hijo (PID {pid})...")
    signal.pause()
    print("[PADRE] Continuando después de recibir la señal")

🏋️‍♂️ Ejercicios
Nivel básico

🔹 Crea un programa donde un proceso hijo notifique al padre usando SIGUSR2.
Nivel intermedio

🔹 Sincronizá dos procesos que se mandan señales mutuamente en forma alternada.
Nivel avanzado

🔹 Combiná señales con multiprocessing.Value o un archivo temporal para verificar que se cumple una condición antes de continuar.
⏸ Puesta en común

    ¿Por qué signal.pause() es útil en sincronización?

    ¿Qué riesgo habría si un proceso espera una señal que nunca llega?

    ¿Qué ventaja tiene usar señales frente a otros mecanismos como sockets o archivos?

📢 Compartí estos avances con el profesor o en tu grupo de estudio.

¿Seguimos con el próximo tema: manejo seguro y async-signal-safe?

¡Claro! Vamos a responder primero las preguntas de puesta en común, y luego avanzamos al siguiente tema: manejo seguro y async-signal-safe.
✅ Respuestas de la puesta en común

    ¿Por qué signal.pause() es útil en sincronización?
    Porque suspende la ejecución del proceso hasta que recibe una señal, lo que evita el uso de ciclos activos (busy-waiting) y permite una forma eficiente de esperar notificaciones externas.

    ¿Qué riesgo habría si un proceso espera una señal que nunca llega?
    El proceso quedaría bloqueado indefinidamente, generando una especie de deadlock si no se maneja correctamente o si no hay un mecanismo de tiempo de espera (timeout) o señal de respaldo.

    ¿Qué ventaja tiene usar señales frente a otros mecanismos como sockets o archivos?
    Las señales son ligeras y rápidas para transmitir eventos simples, no requieren establecer una conexión ni estructuras de datos complejas. Son ideales para notificar eventos, aunque no sirven para transferir datos complejos como los sockets o la memoria compartida.

🔹 Tema 5: Manejo seguro y async-signal-safe
📘 Explicación teórica

Cuando se recibe una señal en un programa, el sistema operativo interrumpe el flujo normal del código y transfiere el control a una función llamada manejador de señal (signal handler).

❗️Sin embargo, no todas las funciones de la biblioteca estándar son seguras para ejecutar dentro de un handler.

Esto se debe a que:

    Las señales pueden interrumpir operaciones que no son reentrantes.

    Si se llama a una función no segura dentro del handler, puede dejar estructuras internas en un estado inconsistente.

Estas funciones seguras se conocen como:
🔐 Funciones async-signal-safe

La lista exacta está definida por POSIX e incluye funciones como:

    write()

    read()

    exit()

    sigaction()

    kill()

Mientras que funciones como printf(), malloc() o cualquier función que use bloqueo o I/O complejos no son seguras dentro de handlers.
🧪 Ejemplo incorrecto

import signal
import time

def handler(sig, frame):
    print("¡Señal recibida!")  # ⚠️ print NO es async-signal-safe en C

signal.signal(signal.SIGUSR1, handler)

print("Esperando señal...")
signal.pause()

Esto funciona en Python por cómo implementa print() (usa bloqueo de intérprete), pero en C esto podría fallar.
✅ Ejemplo seguro (simulado)

En un entorno más estricto, solo deberíamos hacer cosas como:

import signal
import os

def handler(sig, frame):
    os.write(1, b"Señal segura recibida\n")  # ✅ write es async-signal-safe

signal.signal(signal.SIGUSR1, handler)
print("Esperando señal...")
signal.pause()

🏋️‍♂️ Ejercicios
Nivel básico

🔹 Modificá un handler para usar os.write() en lugar de print().
Nivel intermedio

🔹 Simulá una condición donde una señal interrumpe un cálculo. Protegé el handler para que no cause errores.
Nivel avanzado

🔹 Diseñá un esquema de manejo de errores que use señales sin violar la seguridad async-signal-safe (por ejemplo, usando os._exit() en casos críticos).
⏸ Puesta en común

    ¿Por qué no se debe usar print() en un handler en C?

    ¿Qué pasa si un handler llama a malloc()?

    ¿Qué función usarías para imprimir un mensaje dentro de un handler de forma segura?

📢 Recordá compartir estas reflexiones con tu profesor o grupo.

Perfecto. Respondamos las preguntas de puesta en común del tema "Manejo seguro y async-signal-safe" y luego avanzamos al tema 6: Señales en sistemas multihilo.
✅ Respuestas - Puesta en común

    ¿Por qué no se debe usar print() en un handler en C?
    Porque print() no es async-signal-safe: internamente puede usar buffers o mecanismos de I/O que no son reentrantes. Si el handler interrumpe una ejecución que estaba usando esos mismos recursos, puede producirse un comportamiento indefinido.

    ¿Qué pasa si un handler llama a malloc()?
    malloc() tampoco es seguro en contextos asincrónicos. Si el handler interrumpe una asignación de memoria, se pueden corromper estructuras internas del heap, lo que lleva a errores difíciles de depurar como segment faults o fugas de memoria.

    ¿Qué función usarías para imprimir un mensaje dentro de un handler de forma segura?
    En sistemas UNIX, la forma correcta es usar write(fd, buffer, size), ya que write() sí es async-signal-safe. En Python, se puede acceder a ella mediante os.write().

🔹 Tema 6: Señales en sistemas multihilo
📘 Explicación teórica

En un programa con múltiples hilos (threads), el manejo de señales se complica porque:

    Las señales por defecto se entregan a un hilo arbitrario del proceso.

    Algunas señales pueden ser bloqueadas por ciertos hilos y no por otros.

    Se necesita control claro para decidir qué hilo manejará qué señal.

Dos comportamientos comunes:

    Señales como SIGSEGV, SIGINT: se entregan a un solo hilo (el que causó la condición).

    Señales como SIGUSR1: se pueden enviar directamente a un hilo específico (usando funciones de POSIX como pthread_kill()).

☑️ En Python

Python usa el Global Interpreter Lock (GIL), lo que significa:

    Las señales siempre se manejan en el hilo principal (main thread).

    Incluso si otro hilo recibe una señal, el handler registrado se ejecutará en el hilo principal.

    Solo se puede usar signal.signal() desde el hilo principal.

🔧 Ejemplo en Python

import threading
import signal
import os
import time

def handler(sig, frame):
    print(f"[{threading.current_thread().name}] Señal recibida")

def otro_hilo():
    print(f"[{threading.current_thread().name}] En ejecución")
    time.sleep(5)

# Registrar handler (solo desde el main thread)
signal.signal(signal.SIGUSR1, handler)

# Lanzar otro hilo
t = threading.Thread(target=otro_hilo, name="Hilo-secundario")
t.start()

# Enviar señal al proceso
time.sleep(1)
os.kill(os.getpid(), signal.SIGUSR1)

t.join()

📌 Observación: aunque haya un hilo en ejecución, el handler se ejecuta en el main thread.
🏋️‍♂️ Ejercicios
Nivel básico

🔹 Crea un programa multihilo que maneje una señal correctamente desde el hilo principal.
Nivel intermedio

🔹 Intenta registrar un handler desde un hilo secundario. Observá qué error lanza Python.
Nivel avanzado

🔹 Diseñá una arquitectura donde el hilo principal reciba señales y se comunique con los hilos secundarios usando queue.Queue.
⏸ Puesta en común

    ¿Por qué no se pueden registrar handlers con signal.signal() desde un hilo secundario en Python?

    ¿Qué hilo maneja las señales en un programa Python multihilo?

    ¿Cómo comunicarías desde el handler hacia un hilo secundario de forma segura?

📤 Compartí tus respuestas con el profesor y tu equipo.

Perfecto, respondamos primero las preguntas de puesta en común sobre señales en sistemas multihilo, y luego seguimos con el tema 7.
✅ Respuestas – Puesta en común

    ¿Por qué no se pueden registrar handlers con signal.signal() desde un hilo secundario en Python?
    Porque en Python, por diseño del intérprete (y el GIL), solo el hilo principal puede registrar manejadores de señales con signal.signal(). Esto garantiza que todas las señales sean gestionadas de forma predecible y evita conflictos entre hilos.

    ¿Qué hilo maneja las señales en un programa Python multihilo?
    Siempre el hilo principal maneja las señales, incluso si otro hilo provoca la señal o si está activo en ese momento.

    ¿Cómo comunicarías desde el handler hacia un hilo secundario de forma segura?
    Usaría estructuras de comunicación entre hilos como queue.Queue() o threading.Event(), que son seguras para compartir información entre el handler (en el main thread) y los hilos secundarios. De esta forma se evita ejecutar lógica pesada dentro del handler.

🔹 Tema 7: Comparaciones con otros mecanismos de IPC (Inter-Process Communication)
📘 Explicación teórica

Las señales son solo uno de varios mecanismos de IPC en sistemas operativos. Veamos una comparación general:
Mecanismo	Comunicación	Dirección	Velocidad	Complejidad	Casos de uso típicos
Señales	Básica	Unidireccional	Alta	Baja	Notificaciones entre procesos
Pipes (tuberías)	Datos	Unidireccional	Media	Media	Envío de datos entre procesos
Sockets	Datos	Bidireccional	Media/Alta	Alta	Comunicación entre máquinas o procesos
Memoria compartida	Datos	Bidireccional	Muy alta	Alta	Procesamiento rápido entre procesos
Semáforos	Control	N/A	Alta	Media	Sincronización entre procesos o hilos
Queue (multiprocessing)	Datos	Bidireccional	Alta	Baja	Comunicación en Python entre procesos
Ventajas de las señales:

    Rápidas.

    Sencillas de implementar.

    No requieren canales explícitos.

Desventajas:

    Solo envían información muy limitada (número de señal).

    No garantizan orden.

    Su manejo incorrecto puede causar errores sutiles.

🧪 Ejemplo simple comparativo en Python

# Señal (notificación)
import signal, os

def handler(sig, frame):
    print("Recibí SIGUSR1")

signal.signal(signal.SIGUSR1, handler)
os.kill(os.getpid(), signal.SIGUSR1)  # Notificación simple

# Cola (multiprocessing.Queue) para datos
from multiprocessing import Process, Queue

def worker(q):
    q.put("Hola desde el hijo")

q = Queue()
p = Process(target=worker, args=(q,))
p.start()
print(q.get())  # Comunicación con datos
p.join()

🏋️‍♂️ Ejercicios
Nivel básico

🔹 Usá una señal (SIGUSR1) para notificar un evento simple en tu programa.
Nivel intermedio

🔹 Compará el uso de señales con una Queue de multiprocessing: ¿qué ventajas tiene una sobre la otra para sincronización?
Nivel avanzado

🔹 Combiná señales para notificación y una cola para el paso de datos detallados. Simulá una alarma con mensaje.
⏸ Puesta en común

    ¿Qué limitación tienen las señales frente a Queue o Pipes?

    ¿Por qué usarías señales si no permiten enviar datos complejos?

    ¿Qué combinación te parece útil: señales + qué otro mecanismo?

📤 Compartí tus respuestas con el profesor o tu grupo.

¿Querés que avancemos con el último tema del día:
"Preparar un ejercicio funcional que muestre sincronización entre procesos con señales"?

Claro, respondamos primero las preguntas de puesta en común del tema anterior y luego avanzamos al ejercicio funcional final.
✅ Puesta en común – Comparación de señales con otros mecanismos de IPC

    ¿Qué limitación tienen las señales frente a Queue o Pipes?
    Las señales solo pueden transportar información mínima (el número de la señal). No permiten transmitir datos estructurados como mensajes o archivos, ni garantizan orden o confirmación de entrega. En cambio, Queue y Pipes permiten enviar datos complejos de forma controlada.

    ¿Por qué usarías señales si no permiten enviar datos complejos?
    Porque son extremadamente rápidas y útiles para notificaciones simples o interrupciones de ejecución. Por ejemplo, para indicar que un proceso debe finalizar, reiniciar o guardar estado. También funcionan bien en conjunto con otros mecanismos más complejos.

    ¿Qué combinación te parece útil: señales + qué otro mecanismo?
    Una combinación muy práctica es señales + cola (Queue): la señal sirve para notificar que hay algo nuevo, y la cola se usa para transferir los datos. Esto mantiene la eficiencia de las señales sin perder la capacidad de comunicación estructurada.

📤 Te recuerdo compartir tus respuestas con el profesor o el grupo antes de avanzar.
🧩 Último Tema: Ejercicio funcional de sincronización entre procesos con señales
🎯 Objetivo

Implementar un ejercicio donde dos procesos se comuniquen usando señales para coordinar una acción (ej. aviso para imprimir algo, cambiar de estado, o finalizar).
🧠 Concepto aplicado

Este ejercicio demuestra:

    Envío de señales entre procesos (os.kill).

    Manejadores (signal.signal).

    Sincronización entre padre e hijo.

    Cómo evitar hacer lógica compleja dentro del handler.

⚙️ Paso a paso
1. Crear dos procesos: padre e hijo

Usamos multiprocessing.Process.
2. El hijo esperará una señal del padre (SIGUSR1).
3. Cuando el hijo reciba la señal, ejecuta una acción segura (imprimir mensaje o cambiar variable).
📌 Código completo (comentado)

import os
import signal
import time
from multiprocessing import Process, Value

# Variable compartida para saber si se recibió la señal
def hijo(recibido):
    def manejador(sig, frame):
        print("[Hijo] Señal recibida: SIGUSR1")
        recibido.value = 1  # Notifica al proceso que puede continuar

    # Registro de señal
    signal.signal(signal.SIGUSR1, manejador)
    print(f"[Hijo] Esperando señal (PID: {os.getpid()})...")
    
    # Espera activa hasta que reciba señal
    while not recibido.value:
        time.sleep(0.1)

    print("[Hijo] Acción realizada tras recibir la señal.")

def main():
    recibido = Value('i', 0)  # entero compartido entre procesos
    p = Process(target=hijo, args=(recibido,))
    p.start()

    time.sleep(1)
    print(f"[Padre] Enviando SIGUSR1 al hijo (PID: {p.pid})")
    os.kill(p.pid, signal.SIGUSR1)

    p.join()

if __name__ == "__main__":
    main()

🧪 Ejercicios adicionales
Básico

🔹 Cambia la señal por SIGUSR2 y observa el comportamiento.
Intermedio

🔹 Envía dos señales y que el hijo cuente cuántas recibió.
Avanzado

🔹 Usá signal.setitimer() para enviar señales temporizadas que despierten a un proceso.
⏸ Puesta en común final

    ¿Qué función permite que el hijo registre la señal?

    ¿Qué mecanismo se usó para compartir el estado entre padre e hijo?

    ¿Por qué se usó un bucle con sleep en el proceso hijo?

📤 Compartí tus respuestas con el profesor o en clase.