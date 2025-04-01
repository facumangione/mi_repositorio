import os

pid = os.fork()  # Crea un proceso hijo

if pid > 0:
    print(f"Soy el proceso padre. Mi PID es {os.getpid()}, y mi hijo tiene PID {pid}")
else:
    print(f"Soy el proceso hijo. Mi PID es {os.getpid()} y mi padre tiene PID {os.getppid()}")
