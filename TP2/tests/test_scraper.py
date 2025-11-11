
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.async_http import AsyncHTTPClient, fetch_url
from scraper.html_parser import HTMLParser, parse_html
from scraper.metadata_extractor import MetadataExtractor, analyze_seo


# ==================== TESTS DE ASYNC HTTP CLIENT ====================

@pytest.mark.asyncio
async def test_async_client_context_manager():
    async with AsyncHTTPClient() as client:
        assert client.session is not None
    
    # Sesión debe estar cerrada
    assert client.session.closed


@pytest.mark.asyncio
async def test_fetch_simple():
    async with AsyncHTTPClient(timeout=10) as client:
        html, status, metadata = await client.fetch('http://example.com')
        
        assert status == 200
        assert len(html) > 0
        assert 'Example Domain' in html
        assert metadata['final_url']
        assert metadata['content_type']


@pytest.mark.asyncio
async def test_fetch_invalid_url():
    async with AsyncHTTPClient() as client:
        with pytest.raises(ValueError):
            await client.fetch('not-a-valid-url')


@pytest.mark.asyncio
async def test_fetch_timeout():
    async with AsyncHTTPClient(timeout=1) as client:
        with pytest.raises(TimeoutError):
            # URL que tarda mucho
            await client.fetch('http://httpbin.org/delay/10')


@pytest.mark.asyncio
async def test_fetch_multiple():
    urls = [
        'http://example.com',
        'http://example.org',
    ]
    
    async with AsyncHTTPClient(timeout=10) as client:
        results = await client.fetch_multiple(urls)
        
        assert len(results) == len(urls)
        for url in urls:
            assert url in results
            html, status, _ = results[url]
            assert html is not None
            assert status == 200


@pytest.mark.asyncio
async def test_fetch_url_helper():
    html, status = await fetch_url('http://example.com')
    
    assert status == 200
    assert 'Example Domain' in html


# ==================== TESTS DE HTML PARSER ====================

def test_parse_title():
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body></body>
    </html>
    """
    
    result = parse_html(html, 'http://example.com')
    assert result['title'] == 'Test Page'


def test_parse_links():
    html = """
    <html>
        <body>
            <a href="http://example.com/page1">Link 1</a>
            <a href="/page2">Link 2</a>
            <a href="#anchor">Anchor</a>
            <a href="javascript:void(0)">JS Link</a>
        </body>
    </html>
    """
    
    result = parse_html(html, 'http://example.com')
    links = result['links']
    
    # Debe tener 2 links válidos (absoluto y relativo convertido)
    assert len(links) == 2
    assert 'http://example.com/page1' in links
    assert 'http://example.com/page2' in links


def test_parse_meta_tags():
    html = """
    <html>
        <head>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, keywords">
            <meta property="og:title" content="OG Title">
            <meta name="twitter:card" content="summary">
        </head>
    </html>
    """
    
    result = parse_html(html, 'http://example.com')
    meta = result['meta_tags']
    
    assert meta['description'] == 'Test description'
    assert meta['keywords'] == 'test, keywords'
    assert 'open_graph' in meta
    assert meta['open_graph']['og:title'] == 'OG Title'
    assert 'twitter' in meta


def test_parse_structure():
    html = """
    <html>
        <body>
            <h1>Main Title</h1>
            <h2>Subtitle 1</h2>
            <h2>Subtitle 2</h2>
            <h3>Section 1</h3>
            <h3>Section 2</h3>
            <h3>Section 3</h3>
        </body>
    </html>
    """
    
    result = parse_html(html, 'http://example.com')
    structure = result['structure']
    
    assert structure['h1'] == 1
    assert structure['h2'] == 2
    assert structure['h3'] == 3
    assert structure['h4'] == 0


def test_parse_images():
    html = """
    <html>
        <body>
            <img src="http://example.com/img1.jpg">
            <img src="/img2.png">
            <img src="data:image/gif;base64,R0lGOD...">
        </body>
    </html>
    """
    
    result = parse_html(html, 'http://example.com')
    
    assert result['images_count'] == 3
    # Solo 2 URLs válidas (excluye data URI)
    assert len(result['image_urls']) == 2


def test_parse_text_stats():
    html = """
    <html>
        <body>
            <p>This is the first paragraph with some words.</p>
            <p>This is the second paragraph.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
    </html>
    """
    
    result = parse_html(html, 'http://example.com')
    stats = result['text_stats']
    
    assert stats['paragraph_count'] == 2
    assert stats['list_count'] == 1
    assert stats['word_count'] > 0


# ==================== TESTS DE METADATA EXTRACTOR ====================

def test_extract_basic_metadata():
    parsed_data = {
        'title': 'Test Page',
        'links': ['http://example.com/1', 'http://example.com/2'],
        'meta_tags': {},
        'structure': {'h1': 1, 'h2': 2, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
        'images_count': 5,
        'text_stats': {'word_count': 100, 'paragraph_count': 3}
    }
    
    metadata = MetadataExtractor.extract_all(
        parsed_data,
        'https://example.com/test',
        '<html></html>'
    )
    
    assert 'basic' in metadata
    assert metadata['basic']['domain'] == 'example.com'
    assert metadata['basic']['title'] == 'Test Page'


def test_seo_analysis():
    parsed_data = {
        'title': 'Good SEO Title Here',
        'meta_tags': {
            'description': 'This is a good meta description that is within the optimal length range for SEO purposes.',
            'keywords': 'seo, test, optimization'
        },
        'structure': {'h1': 1, 'h2': 3, 'h3': 2, 'h4': 0, 'h5': 0, 'h6': 0},
        'images_count': 5,
        'links': ['http://example.com/1', 'http://example.com/2']
    }
    
    seo = analyze_seo(parsed_data)
    
    assert 'score' in seo
    assert 'grade' in seo
    assert 0 <= seo['score'] <= 100
    assert seo['grade'] in ['A', 'B', 'C', 'D', 'F']


def test_seo_missing_elements():
    parsed_data = {
        'title': '',  # Sin título
        'meta_tags': {},  # Sin meta tags
        'structure': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},  # Sin H1
        'images_count': 0,
        'links': []
    }
    
    seo = analyze_seo(parsed_data)
    
    assert seo['score'] < 50  # Score bajo
    assert len(seo['issues']) > 0  # Debe tener issues
    assert len(seo['recommendations']) > 0


def test_framework_detection():
    html_wordpress = '<html><link href="/wp-content/themes/..."></html>'
    html_react = '<html><div id="root" data-reactroot></div></html>'
    html_bootstrap = '<html><link href="bootstrap.min.css"></html>'
    
    meta_wp = MetadataExtractor._extract_technical(html_wordpress, 'http://example.com')
    meta_react = MetadataExtractor._extract_technical(html_react, 'http://example.com')
    meta_bs = MetadataExtractor._extract_technical(html_bootstrap, 'http://example.com')
    
    assert 'WordPress' in meta_wp['framework_hints']
    assert 'React' in meta_react['framework_hints']
    assert 'Bootstrap' in meta_bs['framework_hints']


# ==================== TEST DE INTEGRACIÓN ====================

@pytest.mark.asyncio
async def test_full_scraping_workflow():
    url = 'http://example.com'
    
    # 1. Fetch
    async with AsyncHTTPClient() as client:
        html, status, http_meta = await client.fetch(url)
    
    assert status == 200
    
    # 2. Parse
    parsed_data = parse_html(html, url)
    
    assert 'title' in parsed_data
    assert 'links' in parsed_data
    assert 'structure' in parsed_data
    
    # 3. Extract metadata
    metadata = MetadataExtractor.extract_all(parsed_data, url, html)
    
    assert 'basic' in metadata
    assert 'seo' in metadata
    assert 'technical' in metadata
    
    # 4. SEO analysis
    seo = analyze_seo(parsed_data)
    
    assert 'score' in seo
    assert seo['score'] > 0


@pytest.mark.asyncio
async def test_parallel_scraping():
    """Test de scraping paralelo de múltiples URLs."""
    urls = [
        'http://example.com',
        'http://example.org',
    ]
    
    async with AsyncHTTPClient() as client:
        results = await client.fetch_multiple(urls)
    
    # Verificar que todas se obtuvieron
    assert len(results) == len(urls)
    
    # Parsear todas
    parsed_results = {}
    for url, (html, status, _) in results.items():
        if html:
            parsed_results[url] = parse_html(html, url)
    
    assert len(parsed_results) == len(urls)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])