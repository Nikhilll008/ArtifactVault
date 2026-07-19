

def paginate_list(items: list, page: int = 1, page_size: int = 9) -> dict:
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = max(1, min(int(page_size), 50))
    except (TypeError, ValueError):
        page_size = 9

    total = len(items)
    total_pages = max(1, -(-total // page_size))  # ceil division
    page = min(page, total_pages)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'results': items[start:end],
    }
