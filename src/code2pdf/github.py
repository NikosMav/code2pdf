"""Lightweight wrapper around the GitHub API."""
from __future__ import annotations

from github import Github


def fetch_profile(username: str, token: str | None = None) -> dict:
    gh = Github(token) if token else Github()
    user = gh.get_user(username)

    data = {
        "name": user.name or user.login,
        "bio": user.bio,
        "location": user.location,
        "public_repos": user.public_repos,
        "followers": user.followers,
        "repos": [],
    }

    for repo in user.get_repos():
        if repo.fork:
            continue
        data["repos"].append(
            dict(
                name=repo.name,
                description=repo.description,
                language=repo.language,
                stars=repo.stargazers_count,
                html_url=repo.html_url,
            )
        )

    # Keep top 10 by stars
    data["repos"] = sorted(data["repos"], key=lambda r: r["stars"], reverse=True)[:10]
    return data