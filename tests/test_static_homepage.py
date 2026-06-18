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

    assert "<title>Yixun Hong</title>" in html
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

    assert labels == [
        "Home",
        "Resume",
        "Full Version",
        "Home",
        "Resume",
        "Full Version",
    ]
    assert hrefs == [
        "/",
        "/resume.html",
        "https://foreverhyx.top/",
        "/",
        "/resume.html",
        "https://foreverhyx.top/",
    ]
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


def test_news_is_replaced_with_github_pages_and_award_items():
    html = read("index.html")

    assert "Homepage redesign launched with new layout." not in html
    assert (
        "<strong>2026.6:</strong> Simplified Homepage deployed on GitHub Pages. "
        "Visit <a href=\"https://foreverhyx.top/\">foreverhyx.top</a> for the full version."
    ) in html
    assert (
        "<strong>2026.5:</strong> ZJU supercomputing team won First Prize and "
        "the Application Innovation Award at ASC26; I served as team captain."
    ) in html
    assert "https://www.zju.edu.cn/english/_t874/2026/0528/c19573a3167250/page.htm" in html
    assert (
        "<strong>2025.11:</strong> Zhejiang University claimed the IndySCC title "
        "after a 46-hour cloud showdown; I contributed as a ZJUSCT team member."
    ) in html
    assert "https://www.zju.edu.cn/english/_t874/2026/0128/c19573a3131853/page.htm" in html


def test_resume_page_mirrors_original_resume_view_with_remote_pdf():
    html = read("resume.html")
    parser = LinkParser()
    parser.feed(html)

    assert "<title>Yixun Hong | Resume</title>" in html
    assert "Resume of Yixun Hong" in html
    assert "&larr; Back to Home" in html
    assert "Yixun Hong &middot; Undergraduate at Zhejiang University" in html
    assert (
        'src="https://foreverhyx.top/uploads/transcript.pdf" '
        'title="Resume PDF" class="resume-pdf-iframe"'
    ) in html
    assert (
        'href="https://foreverhyx.top/uploads/transcript.pdf" '
        'target="_blank" rel="noopener noreferrer" class="link-styled"'
    ) in html

    nav_links = [
        link
        for link in parser.links
        if "nav-link" in link["class"].split()
        or "nav-mobile-link" in link["class"].split()
    ]
    labels = [link["text"].strip() for link in nav_links]
    assert labels == [
        "Home",
        "Resume",
        "Full Version",
        "Home",
        "Resume",
        "Full Version",
    ]


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
