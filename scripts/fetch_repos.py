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

import logging
import os
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PER_PAGE = 100
TIMEOUT = 10


class RepoFetcher:
    def __init__(self, username: str, token: Optional[str] = None) -> None:
        self._username: str = username
        self._headers: Dict[str, str] = {'Accept': 'application/vnd.github+json'}
        if token:
            self._headers['Authorization'] = f'Bearer {token}'
        else:
            logger.warning('No GITHUB_TOKEN provided; falling back to unauthenticated API (60 requests/hour)')

    def _get_paginated(self, url: str) -> List[Dict[str, Any]]:
        """Fetch every page of a list endpoint. GitHub returns 30 items per page by default."""
        items: List[Dict[str, Any]] = []
        page = 1
        while True:
            response = requests.get(
                url, headers=self._headers, params={'per_page': PER_PAGE, 'page': page}, timeout=TIMEOUT
            )
            response.raise_for_status()
            batch = response.json()
            items.extend(batch)
            if len(batch) < PER_PAGE:
                return items
            page += 1

    def _get_repo_prs(self, repo_name: str) -> int:
        url = f'https://api.github.com/repos/{self._username}/{repo_name}/pulls'
        try:
            return len(self._get_paginated(url))
        except requests.RequestException as e:
            logger.error(f'Error fetching PRs for {repo_name}: {e}')
            return 0

    @staticmethod
    def _format_date(date_str: str) -> str:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S') if date_str else ''

    def _fetch_repo_data(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        name = repo.get('name', '')
        return {
            'name': name,
            'description': repo.get('description') or "This repo is awesome! But it doesn't have a description yet.",
            'repo_url': repo.get('html_url', ''),
            'repo_topics': repo.get('topics', []),
            'language': repo.get('language') or '',
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'prs': self._get_repo_prs(name),
            'is_fork': repo.get('fork', False),
            'created_at': self._format_date(repo.get('created_at', '')),
            'updated_at': self._format_date(repo.get('updated_at', '')),
            'pushed_at': self._format_date(repo.get('pushed_at', '')),
            'has_pages': repo.get('has_pages', False),
            'page_url': f'https://{self._username}.github.io/{name}/' if repo.get('has_pages', False) else '',
            'homepage': repo.get('homepage') or '',
            'license': repo['license']['name'] if repo.get('license') else 'No License',
            'size': repo.get('size', 0),
            'visibility': repo.get('visibility', ''),
            'has_issues': repo.get('has_issues', False),
            'open_issues_count': repo.get('open_issues_count', 0),
            'has_discussions': repo.get('has_discussions', False),
        }

    def fetch_repos(self) -> List[Dict[str, Any]]:
        url = f'https://api.github.com/users/{self._username}/repos'
        try:
            repos = self._get_paginated(url)
        except requests.RequestException as e:
            raise RuntimeError(f'Failed to fetch repos for {self._username}: {e}') from e
        logger.info(f'Fetched {len(repos)} repos for {self._username}')
        return [self._fetch_repo_data(repo) for repo in repos]


class RepositoryService:
    def __init__(self) -> None:
        self._username: str = os.getenv('GITHUB_USERNAME', '')
        if not self._username:
            raise RuntimeError('GITHUB_USERNAME is not set')
        self._fetcher = RepoFetcher(self._username, os.getenv('GITHUB_TOKEN') or None)

    def get_repos(self, config: Dict[str, Any]) -> Dict[str, Any]:
        repos = self._fetcher.fetch_repos()
        repos = self._filter_repos(repos, config)
        sort = config.get('repos', {}).get('sort', {})
        repos = self._sort_repos(repos, sort.get('key', 'stars'), sort.get('descending', True))
        repos = self._limit_repos(repos, config)
        return {'all': repos, 'filters': self._get_filters(repos)}

    def _filter_repos(self, repos: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not config['repos'].get('show_forks', False):
            repos = [r for r in repos if not r.get('is_fork', False)]
        excluded = [repo.replace('GITHUB_USERNAME', self._username) for repo in config['repos'].get('exclude', []) or []]
        exclude_patterns = config['repos'].get('exclude_patterns', []) or []
        return [
            repo for repo in repos
            if not any(re.match(pattern, repo.get('name', '')) for pattern in exclude_patterns)
            and repo.get('name', '') not in excluded
        ]

    def _sort_repos(self, repos: List[Dict[str, Any]], sort_key: str, reverse: bool) -> List[Dict[str, Any]]:
        if repos and sort_key not in repos[0]:
            logger.warning(f'Unknown sort key "{sort_key}", falling back to "stars"')
            sort_key = 'stars'
        return sorted(repos, key=lambda r: (r.get(sort_key) is not None, r.get(sort_key)), reverse=reverse)

    def _limit_repos(self, repos: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        limit = config['repos'].get('limit', 0)
        return repos[:limit] if limit > 0 else repos

    def _get_filters(self, repos: List[Dict[str, Any]]) -> List[str]:
        topics: List[str] = []
        for repo in repos:
            topics.extend(repo.get('repo_topics', []))
            if repo.get('language'):
                topics.append(repo['language'])
        return [item for item, _ in Counter(topics).most_common(4) if item]
