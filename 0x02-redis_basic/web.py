#!/usr/bin/env python3
"""Module for implementing an expiring."""
import redis
import requests
from typing import Optional


r = redis.Redis()


def get_page(url: str) -> str:
    """Obtain the HTML content of a particular URL."""
    count_key = f"count:{url}"
    r.incr(count_key)
    cached_html: Optional[bytes] = r.get(url)
    if cached_html:
        return cached_html.decode('utf-8')
    response = requests.get(url)
    html_content = response.text
    r.setex(url, 10, html_content)
    return html_content


if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk"
    print(get_page(test_url))
