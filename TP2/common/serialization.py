import json
import pickle
import base64
from typing import Any, Dict
from enum import Enum


class SerializationFormat(Enum):
    JSON = "json"
    PICKLE = "pickle"


class Serializer:    
    @staticmethod
    def serialize(data: Any, format: SerializationFormat = SerializationFormat.JSON) -> bytes:
        if format == SerializationFormat.JSON:
            return Serializer._serialize_json(data)
        elif format == SerializationFormat.PICKLE:
            return Serializer._serialize_pickle(data)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    @staticmethod
    def deserialize(data: bytes, format: SerializationFormat = SerializationFormat.JSON) -> Any:
        if format == SerializationFormat.JSON:
            return Serializer._deserialize_json(data)
        elif format == SerializationFormat.PICKLE:
            return Serializer._deserialize_pickle(data)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    @staticmethod
    def _serialize_json(data: Any) -> bytes:
        return json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    @staticmethod
    def _deserialize_json(data: bytes) -> Any:
        return json.loads(data.decode('utf-8'))
    
    @staticmethod
    def _serialize_pickle(data: Any) -> bytes:
        return pickle.dumps(data)
    
    @staticmethod
    def _deserialize_pickle(data: bytes) -> Any:
        return pickle.loads(data)


class Base64Helper:    
    @staticmethod
    def encode(data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def decode(data: str) -> bytes:
        return base64.b64decode(data)
    
    @staticmethod
    def encode_image(image_bytes: bytes) -> str:
        return Base64Helper.encode(image_bytes)
    
    @staticmethod
    def decode_image(base64_str: str) -> bytes:
        return Base64Helper.decode(base64_str)


def prepare_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    
    for key, value in data.items():
        if isinstance(value, bytes):
            # Convertir bytes a base64
            result[key] = Base64Helper.encode(value)
        elif isinstance(value, dict):
            # Recursión para diccionarios anidados
            result[key] = prepare_for_json(value)
        elif isinstance(value, list):
            # Procesar listas
            result[key] = [
                prepare_for_json(item) if isinstance(item, dict) 
                else Base64Helper.encode(item) if isinstance(item, bytes)
                else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result