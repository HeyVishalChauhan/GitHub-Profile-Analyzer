import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests


API_URL = "https://api.github.com"
TIMEOUT = 15


def fetch_data(url, params=None):
    """Fetch JSON data from GitHub API."""
    try:
        response = requests.get(
            url,
            params=params,
            timeout=TIMEOUT,
            headers={"Accept": "application/vnd.github+json"}
        )

        if response.status_code == 404:
            print("GitHub user ya resource nahi mila.")
            return None

        if response.status_code == 403:
            print("GitHub API rate limit ho sakti hai. Baad mein try karo.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Request timeout. Dobara try karo.")
    except requests.exceptions.ConnectionError:
        print("Internet connection check karo.")
    except requests.exceptions.RequestException as error:
        print(f"API error: {error}")

    return None


def get_profile(username):
    """Fetch and display GitHub profile."""
    profile = fetch_data(f"{API_URL}/users/{username}")

    if not isinstance(profile, dict):
        return None

    print("\n" + "=" * 50)
    print("             GITHUB PROFILE")
    print("=" * 50)
    print(f"Username      : {profile.get('login', 'N/A')}")
    print(f"Name          : {profile.get('name') or 'Not provided'}")
    print(f"Bio           : {profile.get('bio') or 'Not provided'}")
    print(f"Location      : {profile.get('location') or 'Not provided'}")
    print(f"Followers     : {profile.get('followers', 0)}")
    print(f"Following      : {profile.get('following', 0)}")
    print(f"Public repos  : {profile.get('public_repos', 0)}")
    print(f"Profile URL   : {profile.get('html_url', 'N/A')}")
    print("=" * 50)

    return profile


def get_repositories(username):
    """Fetch public repositories, up to 1000."""
    repositories = []

    for page in range(1, 11):
        data = fetch_data(
            f"{API_URL}/users/{username}/repos",
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page
            }
        )

        if data is None or not isinstance(data, list):
            return None

        repositories.extend(data)

        if len(data) < 100:
            break

    return repositories


def show_statistics(repositories):
    """Display repository statistics."""
    if repositories is None:
        print("Repository data available nahi hai.")
        return

    languages = Counter(
        repo["language"]
        for repo in repositories
        if repo.get("language")
    )

    total_stars = sum(
        repo.get("stargazers_count", 0)
        for repo in repositories
    )

    total_forks = sum(
        repo.get("forks_count", 0)
        for repo in repositories
    )

    print("\n" + "=" * 50)
    print("          DEVELOPER STATISTICS")
    print("=" * 50)
    print(f"Repositories analyzed : {len(repositories)}")
    print(f"Total stars           : {total_stars}")
    print(f"Total forks           : {total_forks}")

    print("\nProgramming Languages:")
    if languages:
        for language, count in languages.most_common():
            print(f"  {language}: {count} repositories")
    else:
        print("  No language data available.")

    top_repositories = sorted(
        repositories,
        key=lambda repo: repo.get("stargazers_count", 0),
        reverse=True
    )

    print("\nTop 5 Repositories:")
    if not top_repositories:
        print("  Koi public repository nahi mili.")
    else:
        for repo in top_repositories[:5]:
            print(
                f"  {repo.get('name', 'N/A')} | "
                f"Stars: {repo.get('stargazers_count', 0)} | "
                f"Forks: {repo.get('forks_count', 0)}"
            )
            print(f"  {repo.get('html_url', '')}")

    print("=" * 50)


def search_repositories(repositories):
    """Search repository names and descriptions."""
    if repositories is None:
        print("Repository data available nahi hai.")
        return

    keyword = input("Search keyword enter karo: ").strip().lower()

    if not keyword:
        print("Keyword empty nahi hona chahiye.")
        return

    matches = [
        repo for repo in repositories
        if keyword in repo.get("name", "").lower()
        or keyword in (repo.get("description") or "").lower()
    ]

    print(f"\nSearch results: {len(matches)}")

    for repo in matches:
        print(
            f"- {repo.get('name', 'N/A')} | "
            f"Stars: {repo.get('stargazers_count', 0)}"
        )
        print(f"  {repo.get('html_url', '')}")


def export_report(profile, repositories):
    """Export profile and repository data to a JSON file."""
    if profile is None or repositories is None:
        print("Report export karne ke liye data available nahi hai.")
        return

    languages = Counter(
        repo["language"]
        for repo in repositories
        if repo.get("language")
    )

    report = {
        "generated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "profile": {
            "username": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "profile_url": profile.get("html_url"),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public_repositories": profile.get("public_repos", 0)
        },
        "statistics": {
            "repositories_analyzed": len(repositories),
            "total_stars": sum(
                repo.get("stargazers_count", 0)
                for repo in repositories
            ),
            "total_forks": sum(
                repo.get("forks_count", 0)
                for repo in repositories
            ),
            "languages": dict(languages)
        },
        "repositories": [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "url": repo.get("html_url"),
                "updated_at": repo.get("updated_at")
            }
            for repo in repositories
        ]
    }

    filename = f"github_report_{profile['login']}.json"

    try:
        Path(filename).write_text(
            json.dumps(report, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"\nReport successfully saved: {filename}")

    except OSError as error:
        print(f"File save error: {error}")


def main():
    print("\n" + "*" * 50)
    print("          GITHUB PROFILE ANALYZER")
    print("*" * 50)

    username = input("GitHub username enter karo: ").strip()

    if not username:
        print("Username khali nahi hona chahiye.")
        return

    profile = get_profile(username)

    if profile is None:
        print("Profile load nahi hui. Username check karo.")
        return

    repositories = get_repositories(username)

    if repositories is None:
        print("Repositories load nahi hui. Dobara try karo.")
        return

    show_statistics(repositories)

    while True:
        print("\n----------- MENU -----------")
        print("1. Search repositories")
        print("2. Show statistics")
        print("3. Export JSON report")
        print("4. Exit")

        choice = input("Option choose karo: ").strip()

        if choice == "1":
            search_repositories(repositories)

        elif choice == "2":
            show_statistics(repositories)

        elif choice == "3":
            export_report(profile, repositories)

        elif choice == "4":
            print("Thank you for using GitHub Profile Analyzer!")
            break

        else:
            print("Invalid option. 1, 2, 3 ya 4 choose karo.")


if __name__ == "__main__":
    main()