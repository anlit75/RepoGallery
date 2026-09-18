"""Regression tests for bugs that shipped in the fork-based versions."""
import os

import pytest
import yaml
from generate_html import HTMLGenerator

TEMPLATES = os.path.join(os.path.dirname(__file__), '..', 'templates', 'v1')

BASE_CONFIG = {
    'site': {
        'title': "Hi, I'm tester",
        'description': 'desc',
        'show_picture': False,
        'theme': 'light',
        'site_icon': '',
    },
    'repos': {
        'use_custom_image': False,
        'random_image': True,
        'random_image_theme': 'Minimal',
        'sort': {'key': 'stars', 'descending': True},
    },
    'footer': {'show': True, 'icons': [], 'href': []},
}

REPO = {
    'name': 'demo',
    'description': 'plain description',
    'repo_url': 'https://github.com/tester/demo',
    'repo_topics': ['python'],
    'language': 'Python',
    'stars': 1, 'forks': 0, 'prs': 0,
    'pushed_at': '', 'updated_at': '', 'created_at': '',
    'homepage': '', 'page_url': '',
}


def build(tmp_path, config_overrides=None, repo_overrides=None, monkeypatch=None):
    config = yaml.safe_load(yaml.safe_dump(BASE_CONFIG))
    for section, values in (config_overrides or {}).items():
        config[section].update(values)

    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.safe_dump(config), encoding='utf-8')

    monkeypatch.setenv('GITHUB_USERNAME', 'tester')
    monkeypatch.setattr(HTMLGenerator, '_get_github_user_info', lambda self: {})

    output = tmp_path / 'public'
    gen = HTMLGenerator(str(config_path), TEMPLATES, str(output), str(tmp_path / 'assets'))
    repo = dict(REPO, **(repo_overrides or {}))
    gen.generate({'all': [repo], 'filters': ['Python']})
    return (output / 'index.html').read_text(encoding='utf-8'), output


def test_repo_description_is_escaped(tmp_path, monkeypatch):
    """Autoescape was off, so repo metadata went into the page as raw HTML."""
    html, _ = build(
        tmp_path,
        repo_overrides={'description': '<script>alert(1)</script>'},
        monkeypatch=monkeypatch,
    )
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html


def test_live_demo_link_is_not_inline_js(tmp_path, monkeypatch):
    """The Live Demo button used onclick="location.href='{{ url }}'" — quote-escapable."""
    html, _ = build(
        tmp_path,
        repo_overrides={'homepage': "https://example.com/x'"},
        monkeypatch=monkeypatch,
    )
    assert 'onclick' not in html
    assert 'class="demo-link"' in html


def test_footer_mail_link_is_not_empty(tmp_path, monkeypatch):
    """The footer mail icon read {{ mail }}, which was never passed, so it rendered mailto:."""
    html, _ = build(tmp_path, monkeypatch=monkeypatch)
    assert 'mailto:611415132@alum.ccu.edu.tw' in html


def test_unknown_random_image_theme_does_not_crash(tmp_path, monkeypatch):
    """random_image_cycles stayed None and the next call raised TypeError."""
    html, _ = build(tmp_path, {'repos': {'random_image_theme': 'Nope'}}, monkeypatch=monkeypatch)
    assert 'project-image-fallback' in html


def test_static_assets_are_published(tmp_path, monkeypatch):
    _, output = build(tmp_path, monkeypatch=monkeypatch)
    for path in ('css/style.css', 'js/main.js', 'img/favicon.png'):
        assert (output / path).exists(), f'{path} missing from the generated site'


def test_sort_direction_reaches_the_page(tmp_path, monkeypatch):
    """config sort.descending was ignored by the front-end sort dropdown."""
    html, _ = build(tmp_path, {'repos': {'sort': {'key': 'name', 'descending': False}}}, monkeypatch=monkeypatch)
    assert 'data-sort-descending="false"' in html
