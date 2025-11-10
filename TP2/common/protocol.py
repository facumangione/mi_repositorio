import json
import struct
import socket
import asyncio
from typing import Dict, Any, Optional


class Protocol:
    HEADER_SIZE = 4  # 4 bytes para longitud del mensaje (uint32)
    MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10 MB máximo
    
    @staticmethod
    def encode_message(data: Dict[str, Any]) -> bytes:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        length = len(json_data)
        
        if length > Protocol.MAX_MESSAGE_SIZE:
            raise ValueError(f"Mensaje demasiado grande: {length} bytes")
        
        # Network byte order (big-endian)
        header = struct.pack('!I', length)
        return header + json_data
    
    @staticmethod
    def decode_message(data: bytes) -> Dict[str, Any]:
        if len(data) < Protocol.HEADER_SIZE:
            raise ValueError(f"Mensaje incompleto: {len(data)} bytes")
        
        # Extraer longitud del header
        length = struct.unpack('!I', data[:Protocol.HEADER_SIZE])[0]
        
        if length > Protocol.MAX_MESSAGE_SIZE:
            raise ValueError(f"Mensaje demasiado grande: {length} bytes")
        
        # Verificar que tenemos el mensaje completo
        expected_total = Protocol.HEADER_SIZE + length
        if len(data) < expected_total:
            raise ValueError(
                f"Mensaje incompleto: esperado {expected_total}, recibido {len(data)}"
            )
        
        # Extraer y deserializar JSON
        json_data = data[Protocol.HEADER_SIZE:Protocol.HEADER_SIZE + length]
        return json.loads(json_data.decode('utf-8'))
    
    # ==================== MÉTODOS ASÍNCRONOS ====================
    
    @staticmethod
    async def send_message_async(writer: asyncio.StreamWriter, data: Dict[str, Any]) -> None:
        message = Protocol.encode_message(data)
        writer.write(message)
        await writer.drain()
    
    @staticmethod
    async def receive_message_async(reader: asyncio.StreamReader) -> Dict[str, Any]:
        # Leer header
        header = await reader.readexactly(Protocol.HEADER_SIZE)
        length = struct.unpack('!I', header)[0]
        
        if length > Protocol.MAX_MESSAGE_SIZE:
            raise ValueError(f"Mensaje demasiado grande: {length} bytes")
        
        # Leer datos
        json_data = await reader.readexactly(length)
        return json.loads(json_data.decode('utf-8'))
    
    # ==================== MÉTODOS SÍNCRONOS ====================
    
    @staticmethod
    def send_message_sync(sock: socket.socket, data: Dict[str, Any]) -> None:
        message = Protocol.encode_message(data)
        sock.sendall(message)
    
    @staticmethod
    def receive_message_sync(sock: socket.socket) -> Dict[str, Any]:
        # Leer header
        header = Protocol._recv_exact(sock, Protocol.HEADER_SIZE)
        length = struct.unpack('!I', header)[0]
        
        if length > Protocol.MAX_MESSAGE_SIZE:
            raise ValueError(f"Mensaje demasiado grande: {length} bytes")
        
        # Leer datos
        json_data = Protocol._recv_exact(sock, length)
        return json.loads(json_data.decode('utf-8'))
    
    @staticmethod
    def _recv_exact(sock: socket.socket, num_bytes: int) -> bytes:
        data = b''
        while len(data) < num_bytes:
            chunk = sock.recv(min(4096, num_bytes - len(data)))
            if not chunk:
                raise ConnectionError("Conexión cerrada por el peer")
            data += chunk
        return data


class MessageType:    
    # Requests
    SCRAPE_REQUEST = "scrape_request"
    SCREENSHOT_REQUEST = "screenshot_request"
    PERFORMANCE_REQUEST = "performance_request"
    IMAGES_REQUEST = "images_request"
    
    # Responses
    SUCCESS_RESPONSE = "success_response"
    ERROR_RESPONSE = "error_response"
    
    # Control
    PING = "ping"
    PONG = "pong"
    SHUTDOWN = "shutdown"


def create_request(msg_type: str, url: str, **kwargs) -> Dict[str, Any]:
    return {
        "type": msg_type,
        "url": url,
        "data": kwargs
    }


def create_response(success: bool, result: Any = None, error: str = None) -> Dict[str, Any]:
    response = {
        "type": MessageType.SUCCESS_RESPONSE if success else MessageType.ERROR_RESPONSE,
        "success": success
    }
    
    if success:
        response["result"] = result
    else:
        response["error"] = error or "Unknown error"
    
    return response