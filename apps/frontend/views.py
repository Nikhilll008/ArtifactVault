"""
CONCEPT: Django
-----------------
This view deliberately does NOT use Django's template-rendering engine
(no `render()` / Template/Context). The pages in templates/ are plain
HTML + vanilla JS — they don't use Django template tags — so instead
we just read the file's raw bytes/text off disk and return them as an
HttpResponse. This sidesteps any risk of Django's `{{ }}` / `{% %}`
template parser tripping over JavaScript code that happens to contain
similar-looking characters.
"""
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, Http404

TEMPLATES_DIR = Path(settings.BASE_DIR) / 'templates'


def serve_page(request, page_name='index'):
    file_path = TEMPLATES_DIR / f'{page_name}.html'
    if not file_path.exists():
        raise Http404(f'{page_name}.html was not found in templates/.')
    html = file_path.read_text(encoding='utf-8')
    return HttpResponse(html, content_type='text/html; charset=utf-8')
