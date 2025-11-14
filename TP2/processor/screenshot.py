import base64
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def generate_screenshot(url: str, options: Dict[str, Any] = None) -> str:
    """
    Genera screenshot usando fallback (PIL) para evitar problemas con Selenium.
    """
    if options is None:
        options = {}
    
    width = options.get('width', 1920)
    height = options.get('height', 1080)
    
    logger.info(f"Generando screenshot fallback de {url}")
    
    return _generate_screenshot_fallback(url, width, height)


def _generate_screenshot_fallback(url: str, width: int, height: int) -> str:
    """Genera imagen placeholder simple y rápida."""
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Crear imagen
    img = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Dibujar borde
    draw.rectangle([(10, 10), (width-10, height-10)], outline='#333333', width=3)
    
    # Texto
    text_lines = [
        "Screenshot Placeholder",
        "",
        f"URL: {url[:60]}",
        "",
        "Para screenshots reales:",
        "1. Instalar: pip install selenium",
        "2. Instalar ChromeDriver",
        "3. Reiniciar servidor"
    ]
    
    y_offset = height // 2 - 100
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = None
    
    for line in text_lines:
        draw.text((50, y_offset), line, fill='#333333', font=font)
        y_offset += 40
    
    # Convertir a base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    logger.info(f"Screenshot fallback generado: {len(screenshot_b64)} chars")
    return screenshot_b64
