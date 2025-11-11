
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


class HTMLParser:
    
    @staticmethod
    def parse(html: str, base_url: str) -> Dict:
        soup = BeautifulSoup(html, 'lxml')
        
        logger.info(f"Parsing HTML from {base_url}")
        
        return {
            "title": HTMLParser._extract_title(soup),
            "links": HTMLParser._extract_links(soup, base_url),
            "meta_tags": HTMLParser._extract_meta_tags(soup),
            "structure": HTMLParser._extract_structure(soup),
            "images_count": len(soup.find_all('img')),
            "image_urls": HTMLParser._extract_image_urls(soup, base_url),
            "text_stats": HTMLParser._extract_text_stats(soup),
            "social_links": HTMLParser._extract_social_links(soup)
        }
    
    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        """Extrae el título de la página."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # Fallback: buscar h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        return ""
    
    @staticmethod
    def _extract_links(soup: BeautifulSoup, base_url: str, limit: int = 100) -> List[str]:
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            
            # Ignorar anchors y javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Convertir a URL absoluta
            try:
                absolute_url = urljoin(base_url, href)
                
                # Solo URLs HTTP/HTTPS
                parsed = urlparse(absolute_url)
                if parsed.scheme in ['http', 'https']:
                    links.add(absolute_url)
            except Exception:
                continue
            
            if len(links) >= limit:
                break
        
        return sorted(list(links))[:limit]
    
    @staticmethod
    def _extract_meta_tags(soup: BeautifulSoup) -> Dict:
        meta_tags = {}
        
        # Description
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc and desc.get('content'):
            meta_tags['description'] = desc['content']
        
        # Keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and keywords.get('content'):
            meta_tags['keywords'] = keywords['content']
        
        # Author
        author = soup.find('meta', attrs={'name': 'author'})
        if author and author.get('content'):
            meta_tags['author'] = author['content']
        
        # Open Graph tags
        og_tags = {}
        for og in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            prop = og.get('property')
            content = og.get('content')
            if prop and content:
                og_tags[prop] = content
        
        if og_tags:
            meta_tags['open_graph'] = og_tags
        
        # Twitter Card tags
        twitter_tags = {}
        for tw in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            name = tw.get('name')
            content = tw.get('content')
            if name and content:
                twitter_tags[name] = content
        
        if twitter_tags:
            meta_tags['twitter'] = twitter_tags
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            meta_tags['canonical'] = canonical['href']
        
        return meta_tags
    
    @staticmethod
    def _extract_structure(soup: BeautifulSoup) -> Dict[str, int]:
        return {
            f"h{i}": len(soup.find_all(f'h{i}'))
            for i in range(1, 7)
        }
    
    @staticmethod
    def _extract_image_urls(soup: BeautifulSoup, base_url: str, limit: int = 20) -> List[str]:
        image_urls = []
        
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            
            # Ignorar data URIs
            if src.startswith('data:'):
                continue
            
            # Convertir a URL absoluta
            try:
                absolute_url = urljoin(base_url, src)
                parsed = urlparse(absolute_url)
                
                if parsed.scheme in ['http', 'https']:
                    image_urls.append(absolute_url)
            except Exception:
                continue
            
            if len(image_urls) >= limit:
                break
        
        return image_urls
    
    @staticmethod
    def _extract_text_stats(soup: BeautifulSoup) -> Dict:
        # Obtener todo el texto visible
        text = soup.get_text(separator=' ', strip=True)
        
        # Contar palabras
        words = text.split()
        word_count = len(words)
        
        # Contar párrafos
        paragraphs = soup.find_all('p')
        paragraph_count = len(paragraphs)
        
        # Contar listas
        lists = soup.find_all(['ul', 'ol'])
        list_count = len(lists)
        
        return {
            "word_count": word_count,
            "paragraph_count": paragraph_count,
            "list_count": list_count,
            "char_count": len(text)
        }
    
    @staticmethod
    def _extract_social_links(soup: BeautifulSoup) -> Dict[str, str]:
        social_patterns = {
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'instagram': ['instagram.com'],
            'linkedin': ['linkedin.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'github': ['github.com'],
            'tiktok': ['tiktok.com']
        }
        
        social_links = {}
        
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            
            for platform, patterns in social_patterns.items():
                if any(pattern in href for pattern in patterns):
                    if platform not in social_links:
                        social_links[platform] = href
                    break
        
        return social_links


def parse_html(html: str, url: str) -> Dict:
    return HTMLParser.parse(html, url)