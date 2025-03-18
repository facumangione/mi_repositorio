
#import sys

#if len(sys.argv) > 1:
#    print("Hola,", sys.argv[1])
#else:
#    print("Uso: python3 saludo.py [nombre]")

#import sys
#import getopt

#def main():
#    try:
#        opts, args = getopt.getopt(sys.argv[1:], "n:e:", ["nombre=", "edad="])
#    except getopt.GetoptError as err:
#        print("Error:", err)
#        print("Uso: python3 saludo.py -n <nombre>")
#        sys.exit(1)

#    nombre = None
#    edad = None
#    for opt, arg in opts:
#        if opt in ("-n", "--nombre"):
#            nombre = arg
#        elif opt in ("-e", "--edad"):
#            edad = arg


#    if nombre and edad:
#        print(f"Hola, {nombre}! Tienes {edad} años.")
#    elif nombre:
#        print(f"Hola, {nombre}!")
#    else:
#        print("Por favor, proporciona un nombre con -n o --nombre.")


#if __name__ == "__main__":
#    main()

import argparse

# 1️⃣ Crear el parser
parser = argparse.ArgumentParser(description="Script de saludo")

# 2️⃣ Agregar un argumento obligatorio
parser.add_argument("-n", "--nombre", required=True, help="Tu nombre")

# 3️⃣ Parsear los argumentos
args = parser.parse_args()

# 4️⃣ Usar el argumento
print(f"Hola, {args.nombre}!")
