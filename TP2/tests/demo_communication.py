import sys
import asyncio
import argparse
from common.protocol import Protocol, MessageType, create_request, create_response

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Cliente conectado desde: {addr}")
    
    try:
        while True:
            # Recibir mensaje
            try:
                message = await Protocol.receive_message_async(reader)
            except asyncio.IncompleteReadError:
                print(f"Cliente {addr} desconectado")
                break
            
            msg_type = message.get('type')
            print(f"Recibido: {msg_type} de {addr}")
            print(f"   Datos: {message}")
            
            # Procesar según tipo
            if msg_type == MessageType.PING:
                # Responder a ping
                response = create_response(True, result={"message": "PONG"})
                print(f"Enviando PONG a {addr}")
            
            elif msg_type == MessageType.SCRAPE_REQUEST:
                # Simular procesamiento
                url = message.get('url', 'unknown')
                print(f"Procesando scraping de: {url}")
                await asyncio.sleep(1)  # Simular trabajo
                
                response = create_response(True, result={
                    "url": url,
                    "title": f"Título de {url}",
                    "links_count": 42,
                    "status": "completed"
                })
            
            elif msg_type == MessageType.SHUTDOWN:
                # Comando de shutdown
                print(f"Comando de shutdown recibido de {addr}")
                response = create_response(True, result={"message": "Shutting down"})
                await Protocol.send_message_async(writer, response)
                break
            
            else:
                # Tipo desconocido
                response = create_response(False, error=f"Unknown message type: {msg_type}")
            
            # Enviar respuesta
            await Protocol.send_message_async(writer, response)
            print(f"Respuesta enviada a {addr}\n")
    
    except Exception as e:
        print(f"Error manejando cliente {addr}: {e}")
    
    finally:
        print(f"Cerrando conexión con {addr}")
        writer.close()
        await writer.wait_closed()


async def run_server(host='127.0.0.1', port=8888):
    print("=" * 60)
    print("SERVIDOR DE DEMOSTRACIÓN")
    print("=" * 60)
    print(f"Escuchando en: {host}:{port}")
    print("Esperando conexiones...\n")
    
    server = await asyncio.start_server(handle_client, host, port)
    
    async with server:
        await server.serve_forever()



async def run_client(host='127.0.0.1', port=8888):
    """Ejecuta el cliente de demostración."""
    print("=" * 60)
    print("CLIENTE DE DEMOSTRACIÓN")
    print("=" * 60)
    print(f"Conectando a: {host}:{port}\n")
    
    try:
        reader, writer = await asyncio.open_connection(host, port)
        print("Conectado al servidor\n")
        
        # Test 1: Ping
        print("Test 1: Enviando PING...")
        ping_msg = {"type": MessageType.PING, "timestamp": "2024-11-10T10:00:00Z"}
        await Protocol.send_message_async(writer, ping_msg)
        
        response = await Protocol.receive_message_async(reader)
        print(f"Respuesta: {response}")
        print()
        
        # Test 2: Scrape Request
        print("Test 2: Enviando SCRAPE_REQUEST...")
        scrape_msg = create_request(
            MessageType.SCRAPE_REQUEST,
            "https://example.com",
            timeout=30
        )
        await Protocol.send_message_async(writer, scrape_msg)
        
        response = await Protocol.receive_message_async(reader)
        print(f"Respuesta: {response}")
        print()
        
        # Test 3: Request con datos grandes
        print("Test 3: Enviando request con datos grandes...")
        large_msg = create_request(
            MessageType.SCRAPE_REQUEST,
            "https://wikipedia.org",
            links=["https://example.com/" + str(i) for i in range(1000)]
        )
        await Protocol.send_message_async(writer, large_msg)
        
        response = await Protocol.receive_message_async(reader)
        print(f"Respuesta recibida (status: {response.get('success')})")
        print()
        
        # Test 4: Mensaje con Unicode
        print("Test 4: Enviando mensaje con Unicode...")
        unicode_msg = create_request(
            MessageType.SCRAPE_REQUEST,
            "https://ejemplo.com/página",
            descripción="Página de prueba 🌍",
            keywords=["español", "中文", "日本語"]
        )
        await Protocol.send_message_async(writer, unicode_msg)
        
        response = await Protocol.receive_message_async(reader)
        print(f"Respuesta: {response}")
        print()
        
        print("Todos los tests completados exitosamente!")
        print("\n Para cerrar el servidor, ejecuta:")
        print("   python demo_communication.py shutdown")
        
    except ConnectionRefusedError:
        print("Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python demo_communication.py server")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if 'writer' in locals():
            writer.close()
            await writer.wait_closed()
            print("\n Conexión cerrada")


async def send_shutdown(host='127.0.0.1', port=8888):
    print(" Enviando comando de shutdown...")
    
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        shutdown_msg = {"type": MessageType.SHUTDOWN}
        await Protocol.send_message_async(writer, shutdown_msg)
        
        response = await Protocol.receive_message_async(reader)
        print(f" Servidor respondió: {response}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f" Error: {e}")



def main():
    parser = argparse.ArgumentParser(description='Demo de comunicación cliente-servidor')
    parser.add_argument('mode', choices=['server', 'client', 'shutdown'],
                       help='Modo de ejecución')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888,
                       help='Puerto (default: 8888)')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'server':
            asyncio.run(run_server(args.host, args.port))
        elif args.mode == 'client':
            asyncio.run(run_client(args.host, args.port))
        elif args.mode == 'shutdown':
            asyncio.run(send_shutdown(args.host, args.port))
    
    except KeyboardInterrupt:
        print("\n\n Interrumpido por el usuario")
        print(" Adiós!")


if __name__ == '__main__':
    main()