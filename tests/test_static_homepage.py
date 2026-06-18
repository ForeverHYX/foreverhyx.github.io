from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.buttons = []
        self.ids = set()
        self._current_anchor = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        element_id = attrs_dict.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag == "a":
            self._current_anchor = {
                "href": attrs_dict.get("href", ""),
                "class": attrs_dict.get("class", ""),
                "text": "",
            }
        if tag == "button":
            self.buttons.append(attrs_dict)

    def handle_endtag(self, tag):
        if tag == "a" and self._current_anchor is not None:
            self.links.append(self._current_anchor)
            self._current_anchor = None

    def handle_data(self, data):
        if self._current_anchor is not None:
            self._current_anchor["text"] += data


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_static_homepage_contains_core_profile_content():
    html = read("index.html")

    assert "Yixun Hong" in html
    assert "洪奕迅" in html
    assert "Student / Researcher" in html
    assert "Zhejiang University" in html
    assert "Information Security" in html
    assert "Computer Architecture" in html
    assert "GPU microarchitecture" in html
    assert "ASC25 Student Supercomputer Challenge" in html
    assert "HPC101" in html


def test_header_is_reduced_to_home_real_homepage_and_theme_toggle():
    html = read("index.html")
    parser = LinkParser()
    parser.feed(html)

    nav_links = [
        link
        for link in parser.links
        if "nav-link" in link["class"].split()
        or "nav-mobile-link" in link["class"].split()
    ]
    labels = [link["text"].strip() for link in nav_links]
    hrefs = [link["href"] for link in nav_links]

    assert labels == ["Home", "foreverhyx.top", "Home", "foreverhyx.top"]
    assert hrefs == ["/", "https://foreverhyx.top/", "/", "https://foreverhyx.top/"]
    assert "themeToggle" in parser.ids
    assert "searchTrigger" not in parser.ids
    assert "inlineSearchInput" not in parser.ids


def test_backend_only_features_and_beian_are_not_in_static_page():
    html = read("index.html")
    lowered = html.lower()

    forbidden = [
        "/articles",
        "/daily",
        "/gallery",
        'href="/upload"',
        "href='/upload'",
        ">upload<",
        "/api/",
        "search...",
        "search dropdown",
        "beian.miit.gov.cn",
        "icp",
        "备案",
        "浙icp",
    ]
    for token in forbidden:
        assert token not in lowered


def test_static_assets_are_self_contained_and_no_search_api_hook_remains():
    required_assets = [
        "static/css/styles.css",
        "static/js/effects/lightfield.js",
        "static/js/effects/liquid-glass.js",
        "static/js/components/site-header.js",
        "uploads/avatar.png",
        "uploads/favicon.png",
        "uploads/zju.png",
    ]
    for asset in required_assets:
        assert (ROOT / asset).is_file(), asset

    source_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "index.html",
            ROOT / "static/js/components/site-header.js",
        ]
    ).lower()
    assert "/api/search-index" not in source_text
    assert "searchtrigger" not in source_text
    assert "inlinesearchinput" not in source_text


def test_search_engine_files_point_to_github_pages_home():
    html = read("index.html")
    robots = read("robots.txt")
    sitemap = read("sitemap.xml")

    assert 'rel="canonical" href="https://foreverhyx.github.io/"' in html
    assert "Sitemap: https://foreverhyx.github.io/sitemap.xml" in robots
    assert "<loc>https://foreverhyx.github.io/</loc>" in sitemap
