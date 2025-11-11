
from typing import Dict, Any, List
from urllib.parse import urlparse
import re
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    
    @staticmethod
    def extract_all(parsed_data: Dict, url: str, html: str) -> Dict[str, Any]:
        return {
            "basic": MetadataExtractor._extract_basic(parsed_data, url),
            "seo": MetadataExtractor._extract_seo(parsed_data),
            "social": MetadataExtractor._extract_social(parsed_data),
            "technical": MetadataExtractor._extract_technical(html, url),
            "content": MetadataExtractor._extract_content_info(parsed_data)
        }
    
    @staticmethod
    def _extract_basic(parsed_data: Dict, url: str) -> Dict:
        parsed_url = urlparse(url)
        
        return {
            "url": url,
            "domain": parsed_url.netloc,
            "path": parsed_url.path,
            "title": parsed_data.get('title', ''),
            "title_length": len(parsed_data.get('title', '')),
        }
    
    @staticmethod
    def _extract_seo(parsed_data: Dict) -> Dict:
        meta = parsed_data.get('meta_tags', {})
        
        seo_data = {
            "has_description": 'description' in meta,
            "has_keywords": 'keywords' in meta,
            "has_canonical": 'canonical' in meta,
        }
        
        # Description
        if 'description' in meta:
            desc = meta['description']
            seo_data['description'] = desc
            seo_data['description_length'] = len(desc)
            seo_data['description_optimal'] = 120 <= len(desc) <= 160
        
        # Keywords
        if 'keywords' in meta:
            keywords = meta['keywords']
            seo_data['keywords'] = keywords.split(',') if ',' in keywords else [keywords]
            seo_data['keywords_count'] = len(seo_data['keywords'])
        
        # Structure
        structure = parsed_data.get('structure', {})
        seo_data['has_h1'] = structure.get('h1', 0) > 0
        seo_data['h1_count'] = structure.get('h1', 0)
        seo_data['multiple_h1'] = structure.get('h1', 0) > 1
        
        # Links
        links = parsed_data.get('links', [])
        seo_data['total_links'] = len(links)
        seo_data['internal_links'] = MetadataExtractor._count_internal_links(
            links, 
            parsed_data.get('basic', {}).get('domain', '')
        )
        
        return seo_data
    
    @staticmethod
    def _extract_social(parsed_data: Dict) -> Dict:
        meta = parsed_data.get('meta_tags', {})
        social_links = parsed_data.get('social_links', {})
        
        social_data = {
            "has_open_graph": 'open_graph' in meta,
            "has_twitter_card": 'twitter' in meta,
            "social_profiles": list(social_links.keys()),
            "social_links": social_links
        }
        
        # Open Graph
        if 'open_graph' in meta:
            og = meta['open_graph']
            social_data['og_title'] = og.get('og:title', '')
            social_data['og_description'] = og.get('og:description', '')
            social_data['og_image'] = og.get('og:image', '')
            social_data['og_type'] = og.get('og:type', '')
        
        # Twitter Card
        if 'twitter' in meta:
            tw = meta['twitter']
            social_data['twitter_card'] = tw.get('twitter:card', '')
            social_data['twitter_site'] = tw.get('twitter:site', '')
        
        return social_data
    
    @staticmethod
    def _extract_technical(html: str, url: str) -> Dict:
        """Información técnica."""
        return {
            "html_size": len(html),
            "html_size_kb": round(len(html) / 1024, 2),
            "uses_https": url.startswith('https'),
            "has_viewport": 'viewport' in html.lower(),
            "has_charset": 'charset' in html.lower(),
            "has_doctype": html.strip().lower().startswith('<!doctype'),
            "framework_hints": MetadataExtractor._detect_frameworks(html)
        }
    
    @staticmethod
    def _extract_content_info(parsed_data: Dict) -> Dict:
        """Información sobre el contenido."""
        text_stats = parsed_data.get('text_stats', {})
        structure = parsed_data.get('structure', {})
        
        return {
            "word_count": text_stats.get('word_count', 0),
            "paragraph_count": text_stats.get('paragraph_count', 0),
            "images_count": parsed_data.get('images_count', 0),
            "links_count": len(parsed_data.get('links', [])),
            "headers_total": sum(structure.values()),
            "structure": structure,
            "reading_time_minutes": max(1, text_stats.get('word_count', 0) // 200)
        }
    
    @staticmethod
    def _count_internal_links(links: List[str], domain: str) -> int:
        """Cuenta enlaces internos (mismo dominio)."""
        if not domain:
            return 0
        
        internal = 0
        for link in links:
            parsed = urlparse(link)
            if parsed.netloc == domain or parsed.netloc == f"www.{domain}":
                internal += 1
        
        return internal
    
    @staticmethod
    def _detect_frameworks(html: str) -> List[str]:
        frameworks = []
        html_lower = html.lower()
        
        patterns = {
            'WordPress': ['wp-content', 'wp-includes'],
            'React': ['react', '__react'],
            'Vue.js': ['vue.js', 'vue.min.js', '__vue'],
            'Angular': ['ng-app', 'angular.js'],
            'Next.js': ['__next', '_next/static'],
            'Bootstrap': ['bootstrap.min.css', 'bootstrap.css'],
            'jQuery': ['jquery.min.js', 'jquery.js'],
            'Tailwind': ['tailwindcss'],
            'Shopify': ['cdn.shopify.com'],
            'Wix': ['wix.com'],
            'Squarespace': ['squarespace.com']
        }
        
        for framework, patterns_list in patterns.items():
            if any(pattern in html_lower for pattern in patterns_list):
                frameworks.append(framework)
        
        return frameworks


def extract_metadata(parsed_data: Dict, url: str, html: str) -> Dict:
    return MetadataExtractor.extract_all(parsed_data, url, html)


def analyze_seo(parsed_data: Dict) -> Dict:
    seo = MetadataExtractor._extract_seo(parsed_data)
    
    # Calcular score (0-100)
    score = 0
    issues = []
    recommendations = []
    
    # Title (20 puntos)
    title = parsed_data.get('title', '')
    if title:
        score += 10
        if 30 <= len(title) <= 60:
            score += 10
        else:
            recommendations.append(f"Title length is {len(title)} chars. Optimal: 30-60 chars")
    else:
        issues.append("Missing page title")
    
    # Description (20 puntos)
    if seo.get('has_description'):
        score += 10
        if seo.get('description_optimal'):
            score += 10
        else:
            recommendations.append("Meta description length not optimal (120-160 chars)")
    else:
        issues.append("Missing meta description")
    
    # H1 (15 puntos)
    if seo.get('has_h1'):
        score += 10
        if not seo.get('multiple_h1'):
            score += 5
        else:
            recommendations.append("Multiple H1 tags found. Use only one H1 per page")
    else:
        issues.append("Missing H1 tag")
    
    # Images (10 puntos)
    images_count = parsed_data.get('images_count', 0)
    if images_count > 0:
        score += 10
    
    # Links (10 puntos)
    if seo.get('total_links', 0) > 0:
        score += 10
    
    # Open Graph (15 puntos)
    if 'open_graph' in parsed_data.get('meta_tags', {}):
        score += 15
    else:
        recommendations.append("Add Open Graph tags for better social media sharing")
    
    # Canonical (10 puntos)
    if seo.get('has_canonical'):
        score += 10
    else:
        recommendations.append("Add canonical URL to avoid duplicate content issues")
    
    return {
        "score": min(score, 100),
        "grade": _score_to_grade(score),
        "issues": issues,
        "recommendations": recommendations,
        "details": seo
    }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"