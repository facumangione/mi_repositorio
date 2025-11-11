
import base64
import logging
from typing import List, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)


def process_images(image_urls: List[str], max_images: int = 5) -> List[Dict[str, Any]]:
    import requests
    from PIL import Image
    
    logger.info(f"Procesando {min(len(image_urls), max_images)} imágenes")
    
    results = []
    
    for i, url in enumerate(image_urls[:max_images]):
        try:
            logger.debug(f"Descargando imagen {i+1}/{max_images}: {url}")
            
            response = requests.get(
                url,
                timeout=5,
                stream=True,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                logger.warning(f"Error descargando {url}: HTTP {response.status_code}")
                continue
            
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            
            original_size = img.size
            img_format = img.format or 'UNKNOWN'
            
            thumbnail_data = create_thumbnail(img, size=(150, 150))
            
            metadata = extract_image_metadata(img)
            
            result = {
                "url": url,
                "thumbnail": thumbnail_data,
                "original_size": {
                    "width": original_size[0],
                    "height": original_size[1]
                },
                "thumbnail_size": {
                    "width": 150,
                    "height": 150
                },
                "format": img_format,
                "size_bytes": len(img_data),
                "mode": img.mode,
                **metadata
            }
            
            results.append(result)
            logger.debug(f"Imagen procesada: {url}")
            
        except requests.Timeout:
            logger.warning(f"Timeout descargando {url}")
            continue
            
        except requests.RequestException as e:
            logger.warning(f"Error de red descargando {url}: {e}")
            continue
            
        except Exception as e:
            logger.warning(f"Error procesando {url}: {e}")
            continue
    
    logger.info(f"Procesadas {len(results)} de {len(image_urls)} imágenes")
    return results


def create_thumbnail(img: 'Image.Image', size: tuple = (150, 150)) -> str:
    from PIL import Image
    
    thumb = img.copy()
    
    thumb.thumbnail(size, Image.Resampling.LANCZOS)
    
    if thumb.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', thumb.size, (255, 255, 255))
        if thumb.mode == 'P':
            thumb = thumb.convert('RGBA')
        background.paste(thumb, mask=thumb.split()[-1] if thumb.mode == 'RGBA' else None)
        thumb = background
    
    buffer = BytesIO()
    thumb.save(buffer, format='PNG', optimize=True)
    
    thumbnail_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return thumbnail_b64


def extract_image_metadata(img: 'Image.Image') -> Dict[str, Any]:
    metadata = {}
    
    try:
        exif = img._getexif()
        if exif:
            metadata['has_exif'] = True
            for tag_id, tag_name in [(271, 'camera_make'), (272, 'camera_model')]:
                if tag_id in exif:
                    metadata[tag_name] = str(exif[tag_id])
        else:
            metadata['has_exif'] = False
    except:
        metadata['has_exif'] = False
    
    try:
        if img.mode == 'RGB':
            colors = img.getcolors(maxcolors=1000000)
            if colors:
                dominant_color = max(colors, key=lambda x: x[0])[1]
                metadata['dominant_color'] = {
                    'r': dominant_color[0],
                    'g': dominant_color[1],
                    'b': dominant_color[2]
                }
    except:
        pass
    
    return metadata


def optimize_image(image_data: bytes, quality: int = 85, max_size: tuple = None) -> bytes:
    from PIL import Image
    
    img = Image.open(BytesIO(image_data))
    
    if max_size and (img.size[0] > max_size[0] or img.size[1] > max_size[1]):
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[-1])
        img = background
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    
    return buffer.getvalue()


def batch_process_images(image_urls: List[str], operations: List[str]) -> Dict[str, Any]:
    results = {
        'thumbnails': [],
        'optimized': [],
        'metadata': []
    }
    
    if 'thumbnail' in operations:
        results['thumbnails'] = process_images(image_urls, max_images=10)
    
    
    return results