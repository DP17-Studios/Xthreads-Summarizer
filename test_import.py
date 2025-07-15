try:
    from firecrawl_py import FirecrawlApp
    print('Imported from firecrawl_py successfully')
except ImportError as e:
    print(f'Import failed: {e}')

try:
    from firecrawl import FirecrawlApp
    print('Imported from firecrawl successfully')
except ImportError as e:
    print(f'Import failed: {e}')
