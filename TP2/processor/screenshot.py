"""
Generación de screenshots usando Selenium.
Este worker se ejecuta en un proceso separado (CPU/IO-bound).
"""
import base64
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def generate_screenshot(url: str, options: Dict[str, Any] = None) -> str:
    """
    Genera screenshot de la URL y retorna imagen en base64.
    Esta función se ejecuta en un proceso separado.
    
    Args:
        url: URL de la página a capturar
        options: Opciones adicionales (timeout, resolution, etc.)
        
    Returns:
        str: Imagen PNG en base64
        
    Raises:
        Exception: Si no se puede generar el screenshot
    """
    if options is None:
        options = {}
    
    timeout = options.get('timeout', 10)
    width = options.get('width', 1920)
    height = options.get('height', 1080)
    
    logger.info(f"Generando screenshot de {url}")
    
    # Intentar usar Selenium primero
    try:
        return _generate_screenshot_selenium(url, timeout, width, height)
    except ImportError:
        logger.warning("Selenium no disponible, usando fallback")
        return _generate_screenshot_fallback(url, width, height)
    except Exception as e:
        logger.error(f"Error con Selenium: {e}, usando fallback")
        return _generate_screenshot_fallback(url, width, height)


def _generate_screenshot_selenium(url: str, timeout: int, width: int, height: int) -> str:
    """Genera screenshot usando Selenium."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, WebDriverException
    
    driver = None
    
    try:
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--window-size={width},{height}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(timeout)
        
        # Cargar página
        driver.get(url)
        
        # Esperar un poco para que renderice
        time.sleep(2)
        
        # Capturar screenshot
        screenshot = driver.get_screenshot_as_png()
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        logger.info(f"Screenshot generado: {len(screenshot_b64)} bytes (base64)")
        return screenshot_b64
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def _generate_screenshot_fallback(url: str, width: int, height: int) -> str:
    """
    Fallback: genera un screenshot "dummy" cuando Selenium no está disponible.
    """
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Crear imagen simple con el URL
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dibujar texto
    text_lines = [
        "Screenshot Placeholder",
        "",
        f"URL: {url}",
        "",
        "Install Selenium + ChromeDriver",
        "for real screenshots"
    ]
    
    y_offset = 50
    for line in text_lines:
        draw.text((50, y_offset), line, fill='black')
        y_offset += 30
    
    # Convertir a base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    logger.info(f"Screenshot fallback generado para {url}")
    return screenshot_b64