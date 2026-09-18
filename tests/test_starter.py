"""The starter files in examples/ are what every new user copies.

These run the generator the way the action does from a user's repository: the
config and assets come from the workspace, the templates from a separate
action path. demo.yml cannot cover this, because `uses: ./` makes those two
directories the same one.
"""
import os
import re
import shutil

import pytest
import yaml
from generate_html import HTMLGenerator

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
STARTER = os.path.join(REPO_ROOT, 'examples', 'starter')
TEMPLATES = os.path.join(REPO_ROOT, 'templates', 'v1')

# Named RepoGallery on purpose: most users keep that name, so a stale mapping
# in the starter's custom_image.yaml would hit them and nobody else.
REPO = {
    'name': 'RepoGallery',
    'description': 'my gallery',
    'repo_url': 'https://github.com/someuser/RepoGallery',
    'repo_topics': ['python'], 'language': 'Python',
    'stars': 5, 'forks': 0, 'prs': 0,
    'pushed_at': '', 'updated_at': '', 'created_at': '',
    'homepage': '', 'page_url': '',
}


@pytest.fixture
def site(tmp_path, monkeypatch):
    """Generate a site from the starter files, as a user's repository would."""
    shutil.copy(os.path.join(STARTER, 'config.yaml'), tmp_path / 'config.yaml')
    shutil.copytree(os.path.join(STARTER, 'assets'), tmp_path / 'assets')

    monkeypatch.setenv('GITHUB_USERNAME', 'someuser')
    monkeypatch.setattr(HTMLGenerator, '_get_github_user_info', lambda self: {})

    output = tmp_path / 'public'
    gen = HTMLGenerator(str(tmp_path / 'config.yaml'), TEMPLATES, str(output), str(tmp_path / 'assets'))
    gen.generate({'all': [REPO], 'filters': ['Python']})
    return output


def test_every_local_reference_resolves(site):
    """A path in the starter that does not exist in the output is a broken page."""
    html = (site / 'index.html').read_text(encoding='utf-8')
    refs = re.findall(r'(?:src|href)="([^"]+)"', html)
    local = [r for r in refs if not r.startswith(('http', 'mailto:', '#'))]

    assert local, 'expected the page to reference its own css/js'
    missing = [r for r in local if not (site / r).exists()]
    assert not missing, f'referenced but not published: {missing}'


def test_starter_ships_no_active_custom_image(site):
    """custom_image.yaml is an example; a real mapping points at a file users do not have."""
    mapping = yaml.safe_load((site / 'assets' / 'custom_image.yaml').read_text(encoding='utf-8'))
    assert not mapping, f'starter maps images that users will not have: {mapping}'


def test_templates_come_from_the_action_not_the_workspace(site, tmp_path):
    """The workspace has no templates/; css, js and the default icon must still land."""
    assert not (tmp_path / 'templates').exists()
    for path in ('css/style.css', 'js/main.js', 'img/favicon.png'):
        assert (site / path).exists(), f'{path} was not taken from the action path'
