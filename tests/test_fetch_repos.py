"""Regression tests for the GitHub API layer."""
import fetch_repos
import pytest
from fetch_repos import RepoFetcher


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_fetch_repos_follows_pagination(monkeypatch):
    """Only the first 30 repos were ever fetched: no per_page, no paging."""
    pages = {1: [{'name': f'r{i}'} for i in range(100)], 2: [{'name': 'last'}]}
    seen = []

    def fake_get(url, headers=None, params=None, timeout=None):
        seen.append(params)
        return FakeResponse(pages[params['page']])

    monkeypatch.setattr(fetch_repos.requests, 'get', fake_get)
    fetcher = RepoFetcher('tester', token='t')
    items = fetcher._get_paginated('https://api.github.com/users/tester/repos')

    assert len(items) == 101
    assert [p['page'] for p in seen] == [1, 2]
    assert all(p['per_page'] == 100 for p in seen)


def test_token_is_sent_on_every_request():
    """PR counts were fetched unauthenticated, so they hit the 60/hour limit and fell back to 0."""
    fetcher = RepoFetcher('tester', token='secret')
    assert fetcher._headers['Authorization'] == 'Bearer secret'


def test_works_without_token():
    fetcher = RepoFetcher('tester', token=None)
    assert 'Authorization' not in fetcher._headers
