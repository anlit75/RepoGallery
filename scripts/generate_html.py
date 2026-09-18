# ------------------------------------------------------------------------------
# Copyright 2025 Ting-An Cheng
#   ____                        ____         _  _
#  |  _ \   ___  _ __    ___   / ___|  __ _ | || |  ___  _ __  _   _
#  | |_) | / _ \| '_ \  / _ \ | |  _  / _` || || | / _ \| '__|| | | |
#  |  _ < |  __/| |_) || (_) || |_| || (_| || || ||  __/| |   | |_| |
#  |_| \_\ \___|| .__/  \___/  \____| \__,_||_||_| \___||_|    \__, |
#               |_|                                            |___/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import argparse
import itertools
import logging
import os
import random
import shutil
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import jinja2
import requests
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIRS = ('css', 'js', 'img')
DEFAULT_SITE_ICON = 'img/favicon.png'


def load_yaml(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise SystemExit(f'Config file not found: {path}')
    except yaml.YAMLError as e:
        raise SystemExit(f'Could not parse {path}: {e}')


class HTMLGenerator:
    def __init__(self, config_path: str, templates_dir: str, output_dir: str, assets_dir: str) -> None:
        self._config: Dict[str, Any] = load_yaml(config_path)
        self._templates_dir = templates_dir
        self._output_dir = output_dir
        self._assets_dir = assets_dir
        self._username: str = os.getenv('GITHUB_USERNAME', '')

        self._custom_images: Dict[str, str] = {}
        if self._repos_cfg('use_custom_image', False):
            custom_path = os.path.join(os.path.dirname(config_path) or '.', 'assets', 'custom_image.yaml')
            if os.path.exists(custom_path):
                self._custom_images = load_yaml(custom_path)
            else:
                logger.warning(f'use_custom_image is on but {custom_path} was not found')

        if not os.path.isdir(templates_dir):
            raise SystemExit(f'Template folder not found: {templates_dir}')
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(['html']),
        )
        self._env.globals.update(zip=zip)
        try:
            self._card_template = self._env.get_template('card_template.html')
            self._site_template = self._env.get_template('site_template.html')
        except jinja2.TemplateNotFound as e:
            raise SystemExit(f'Template file not found in {templates_dir}: {e}')

        self._random_image_cycles: Optional[Dict[str, Any]] = None

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def _site_cfg(self, key: str, default: Any = None) -> Any:
        return self._config.get('site', {}).get(key, default)

    def _repos_cfg(self, key: str, default: Any = None) -> Any:
        return self._config.get('repos', {}).get(key, default)

    def _get_github_user_info(self) -> Dict[str, Any]:
        url = f'https://api.github.com/users/{self._username}'
        headers = {'Accept': 'application/vnd.github+json'}
        token = os.getenv('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'Bearer {token}'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'Error fetching GitHub user info: {e}')
            return {}

    def _set_random_image_cycles(self) -> None:
        theme = str(self._repos_cfg('random_image_theme', 'Minimal'))
        images_ref = load_yaml(os.path.join(self._templates_dir, 'images.yaml'))
        images_list = images_ref.get(theme.capitalize(), [])
        if not images_list:
            logger.warning(f'No images found for theme "{theme}"; falling back to text cards')
            return

        logger.info(f'Found {len(images_list)} images for theme: {theme}')
        random.shuffle(images_list)
        self._random_image_cycles = {
            'image': itertools.cycle([i.get('url', '') for i in images_list]),
            'display_url': itertools.cycle([i.get('display_url', '') for i in images_list]),
            'author': itertools.cycle([i.get('author', '') for i in images_list]),
        }

    def _select_image_for_repo(self, repo: Dict[str, Any]) -> Dict[str, str]:
        if self._repos_cfg('use_custom_image', False):
            custom = self._custom_images.get(repo.get('name', ''), '')
            if custom:
                return {'image': custom, 'display_url': '', 'author': ''}

        if self._random_image_cycles:
            return {key: next(cycle) for key, cycle in self._random_image_cycles.items()}

        return {'image': '', 'display_url': '', 'author': ''}

    def _render_cards(self, repos: List[Dict[str, Any]]) -> str:
        if self._repos_cfg('random_image', True):
            self._set_random_image_cycles()

        return ''.join(
            self._card_template.render(
                repo=repo,
                url=repo.get('homepage') or repo.get('page_url', ''),
                image_data=self._select_image_for_repo(repo),
            ) for repo in repos
        )

    def _copy_static(self) -> None:
        os.makedirs(self._output_dir, exist_ok=True)
        for name in STATIC_DIRS:
            src = os.path.join(self._templates_dir, name)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(self._output_dir, name), dirs_exist_ok=True)

        if os.path.isdir(self._assets_dir):
            shutil.copytree(self._assets_dir, os.path.join(self._output_dir, 'assets'), dirs_exist_ok=True)
            logger.info(f'Copied {self._assets_dir}/ into the site')

    def generate(self, repo_data: Dict[str, Any]) -> None:
        repos = repo_data.get('all', [])
        cards_html = self._render_cards(repos)
        github_info = self._get_github_user_info()

        author = self._site_cfg('author') or self._username
        email = self._site_cfg('email') or github_info.get('email') or ''
        user_img = self._site_cfg('picture_path') or github_info.get('avatar_url', '')

        full_html = self._site_template.render(
            build_time=datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            theme=self._site_cfg('theme', 'light'),
            site_icon=self._site_cfg('site_icon') or DEFAULT_SITE_ICON,
            username=self._username,
            author=author,
            email=email,
            title=str(self._site_cfg('title', '')).replace('GITHUB_USERNAME', self._username),
            description=self._site_cfg('description', ''),
            user_img=user_img if self._site_cfg('show_picture', False) else '',
            cards_html=cards_html,
            sort_key=self._config.get('repos', {}).get('sort', {}).get('key', 'stars'),
            sort_descending=self._config.get('repos', {}).get('sort', {}).get('descending', True),
            filters=repo_data.get('filters', []),
            footer={
                'show': self._config.get('footer', {}).get('show', True),
                'icons': self._config.get('footer', {}).get('icons', []) or [],
                'href': self._config.get('footer', {}).get('href', []) or [],
            },
        )

        self._copy_static()
        output_file = os.path.join(self._output_dir, 'index.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        logger.info(f'Wrote {output_file} ({len(repos)} repos)')


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a RepoGallery site.')
    parser.add_argument('--config', default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--templates', required=True, help='Path to the template folder')
    parser.add_argument('--output', default='public', help='Directory to write the site into')
    parser.add_argument('--assets', default='assets', help='Directory of user assets to publish')
    args = parser.parse_args()

    from fetch_repos import RepositoryService

    generator = HTMLGenerator(args.config, args.templates, args.output, args.assets)
    generator.generate(RepositoryService().get_repos(generator.config))


if __name__ == '__main__':
    main()
