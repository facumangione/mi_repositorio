import pytest
import asyncio
import socket
import threading
import time
from common.protocol import Protocol, MessageType, create_request, create_response
from common.serialization import Serializer, Base64Helper, prepare_for_json

def test_encode_decode_simple():
    data = {"type": "test", "message": "hello"}
    encoded = Protocol.encode_message(data)
    decoded = Protocol.decode_message(encoded)
    
    assert decoded == data


def test_encode_decode_unicode():
    data = {
        "título": "Página de Prueba",
        "descripción": "Hola 世界 🌍",
        "keywords": ["español", "中文", "emoji"]
    }
    
    encoded = Protocol.encode_message(data)
    decoded = Protocol.decode_message(encoded)
    
    assert decoded == data


def test_encode_decode_large_message():
    data = {
        "type": "scrape_result",
        "links": ["https://example.com/very/long/path/to/resource/" + str(i) for i in range(15000)],
        "content": "x" * 700000
    }
    
    encoded = Protocol.encode_message(data)
    decoded = Protocol.decode_message(encoded)
    
    assert decoded == data
    assert len(encoded) > 500_000, f"Mensaje debería ser >500KB, pero es {len(encoded)} bytes"


def test_message_too_large():
    huge_data = {"content": "x" * (Protocol.MAX_MESSAGE_SIZE + 1)}
    
    with pytest.raises(ValueError, match="demasiado grande"):
        Protocol.encode_message(huge_data)


def test_incomplete_message():
    data = {"type": "test"}
    encoded = Protocol.encode_message(data)
    
    incomplete = encoded[:len(encoded) // 2]
    
    with pytest.raises(ValueError, match="incompleto"):
        Protocol.decode_message(incomplete)


def test_create_request():
    req = create_request(
        MessageType.SCRAPE_REQUEST,
        "https://example.com",
        timeout=30
    )
    
    assert req["type"] == MessageType.SCRAPE_REQUEST
    assert req["url"] == "https://example.com"
    assert req["data"]["timeout"] == 30


def test_create_success_response():
    resp = create_response(True, result={"title": "Example"})
    
    assert resp["success"] is True
    assert resp["type"] == MessageType.SUCCESS_RESPONSE
    assert resp["result"]["title"] == "Example"


def test_create_error_response():
    resp = create_response(False, error="Connection timeout")
    
    assert resp["success"] is False
    assert resp["type"] == MessageType.ERROR_RESPONSE
    assert "timeout" in resp["error"].lower()


@pytest.mark.asyncio
async def test_async_send_receive():
    received_data = None
    
    async def server_handler(reader, writer):
        nonlocal received_data
        received_data = await Protocol.receive_message_async(reader)
        
        response = create_response(True, result={"status": "received"})
        await Protocol.send_message_async(writer, response)
        
        writer.close()
        await writer.wait_closed()
    
    # Iniciar servidor
    server = await asyncio.start_server(server_handler, '127.0.0.1', 9999)
    
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 9999)
        
        request = create_request(MessageType.SCRAPE_REQUEST, "https://example.com")
        await Protocol.send_message_async(writer, request)
        
        response = await Protocol.receive_message_async(reader)
        
        
        assert received_data is not None
        assert received_data["type"] == MessageType.SCRAPE_REQUEST
        assert response["success"] is True
        
        writer.close()
        await writer.wait_closed()
    
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_async_multiple_messages():
    messages_received = []
    
    async def server_handler(reader, writer):
        for _ in range(3):
            msg = await Protocol.receive_message_async(reader)
            messages_received.append(msg)
            
            response = create_response(True, result={"count": len(messages_received)})
            await Protocol.send_message_async(writer, response)
        
        writer.close()
        await writer.wait_closed()
    
    server = await asyncio.start_server(server_handler, '127.0.0.1', 9998)
    
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 9998)
        
        for i in range(3):
            request = create_request(MessageType.PING, "test", number=i)
            await Protocol.send_message_async(writer, request)
            
            response = await Protocol.receive_message_async(reader)
            assert response["result"]["count"] == i + 1
        
        assert len(messages_received) == 3
        
        writer.close()
        await writer.wait_closed()
    
    finally:
        server.close()
        await server.wait_closed()


def test_sync_send_receive():
    received_data = None
    
    def server_thread():
        nonlocal received_data
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('127.0.0.1', 9997))
        server_sock.listen(1)
        
        conn, addr = server_sock.accept()
        
        received_data = Protocol.receive_message_sync(conn)
        
        response = create_response(True, result={"status": "ok"})
        Protocol.send_message_sync(conn, response)
        
        conn.close()
        server_sock.close()
    
    server = threading.Thread(target=server_thread, daemon=True)
    server.start()
    time.sleep(0.1)  # Esperar a que el servidor inicie
    
    
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 9997))
    
    request = create_request(MessageType.SCREENSHOT_REQUEST, "https://example.com")
    Protocol.send_message_sync(client_sock, request)
    
    response = Protocol.receive_message_sync(client_sock)
    
    client_sock.close()
    server.join(timeout=2)
    
    assert received_data is not None
    assert received_data["type"] == MessageType.SCREENSHOT_REQUEST
    assert response["success"] is True



def test_base64_encoding():
    data = b"Hello, World! \x00\x01\x02"
    encoded = Base64Helper.encode(data)
    decoded = Base64Helper.decode(encoded)
    
    assert isinstance(encoded, str)
    assert decoded == data


def test_prepare_for_json():
    data = {
        "text": "normal text",
        "image": b"\x89PNG\r\n\x1a\n",  # bytes
        "nested": {
            "binary": b"binary data"
        },
        "list": [b"item1", "item2", {"key": b"value"}]
    }
    
    prepared = prepare_for_json(data)
    
    assert isinstance(prepared["image"], str)
    assert isinstance(prepared["nested"]["binary"], str)
    assert isinstance(prepared["list"][0], str)
    assert prepared["text"] == "normal text"  # Sin cambios
    assert prepared["list"][1] == "item2"  # Sin cambios


@pytest.mark.asyncio
async def test_ipv6_communication():
    async def server_handler(reader, writer):
        msg = await Protocol.receive_message_async(reader)
        response = create_response(True, result=msg)
        await Protocol.send_message_async(writer, response)
        writer.close()
        await writer.wait_closed()
    
    try:
        server = await asyncio.start_server(server_handler, '::1', 9996)
        
        reader, writer = await asyncio.open_connection('::1', 9996)
        
        request = create_request(MessageType.PING, "test")
        await Protocol.send_message_async(writer, request)
        
        response = await Protocol.receive_message_async(reader)
        assert response["success"] is True
        
        writer.close()
        await writer.wait_closed()
        
        server.close()
        await server.wait_closed()
    
    except OSError:
        pytest.skip("IPv6 no disponible en este sistema")


@pytest.mark.asyncio
async def test_concurrent_clients():
    client_count = 10
    results = []
    
    async def server_handler(reader, writer):
        msg = await Protocol.receive_message_async(reader)
        response = create_response(True, result={"received": msg["data"]["client_id"]})
        await Protocol.send_message_async(writer, response)
        writer.close()
        await writer.wait_closed()
    
    server = await asyncio.start_server(server_handler, '127.0.0.1', 9995)
    
    async def client_task(client_id):
        reader, writer = await asyncio.open_connection('127.0.0.1', 9995)
        request = create_request(MessageType.PING, "test", client_id=client_id)
        await Protocol.send_message_async(writer, request)
        response = await Protocol.receive_message_async(reader)
        writer.close()
        await writer.wait_closed()
        return response["result"]["received"]
    
    try:
        tasks = [client_task(i) for i in range(client_count)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == client_count
        assert set(results) == set(range(client_count))
    
    finally:
        server.close()
        await server.wait_closed()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])