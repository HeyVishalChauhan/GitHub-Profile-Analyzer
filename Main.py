import requests
from collections import Counter
from datetime import datetime


API_BASE_URL = "https://api.github.com"


def fetch_data(url, params=None):
    """Fetch JSON data from GitHub API."""
    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
            headers={"Accept": "application/vnd.github+json"}
        )

        if response.status_code == 404:
            print("GitHub user ya resource nahi mila.")
            return None

        if response.status_code == 403:
            print("API rate limit ho sakti hai. Thodi der baad try karo.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Request timeout. Internet check karke dobara try karo.")
    except requests.exceptions.ConnectionError:
        print("Internet connection check karo.")
    except requests.exceptions.RequestException as error:
        print(f"API error: {error}")

    return None


def get_github_profile(username):
    """Get and display GitHub profile details."""
    url = f"{API_BASE_URL}/users/{username}"
    profile = fetch_data(url)

    if not profile:
        return None

    print("\n" + "=" * 48)
    print("             GITHUB PROFILE")
    print("=" * 48)
    print(f"Username          : {profile.get('login', 'N/A')}")
    print(f"Name              : {profile.get('name') or 'Not provided'}")
    print(f"Bio               : {profile.get('bio') or 'Not provided'}")
    print(f"Location          : {profile.get('location') or 'Not provided'}")
    print(f"Public repositories: {profile.get('public_repos', 0)}")
    print(f"Followers         : {profile.get('followers', 0)}")
    print(f"Following         : {profile.get('following', 0)}")
    print(f"Profile URL       : {profile.get('html_url', 'N/A')}")
    print("=" * 48)

    return profile


def get_repositories(username):
    """Fetch and display public repositories."""
    url = f"{API_BASE_URL}/users/{username}/repos"
    params = {
        "sort": "updated",
        "direction": "desc",
        "per_page": 100
    }

    repositories = fetch_data(url, params)

    if repositories is None:
        return None

    if not isinstance(repositories, list):
        print("Unexpected API response.")
        return None

    print("\n" + "=" * 48)
    print("             PUBLIC REPOSITORIES")
    print("=" * 48)

    if not repositories:
        print("Koi public repository nahi mili.")
        return repositories

    for number, repo in enumerate(repositories, start=1):
        updated_at = repo.get("updated_at")

        if updated_at:
            try:
                updated_at = datetime.fromisoformat(
                    updated_at.replace("Z", "+00:00")
                ).strftime("%d %b %Y")
            except ValueError:
                pass
        else:
            updated_at = "N/A"

        print(f"\n{number}. {repo.get('name', 'N/A')}")
        print(f"   Description : {repo.get('description') or 'No description'}")
        print(f"   Language    : {repo.get('language') or 'Not specified'}")
        print(f"   Stars       : {repo.get('stargazers_count', 0)}")
        print(f"   Forks       : {repo.get('forks_count', 0)}")
        print(f"   Updated     : {updated_at}")
        print(f"   URL         : {repo.get('html_url', 'N/A')}")

    return repositories


def show_statistics(repositories):
    """Calculate repository statistics."""
    if repositories is None:
        print("\nStatistics calculate nahi kar sakte.")
        return

    total_repos = len(repositories)
    total_stars = sum(
        repo.get("stargazers_count", 0) for repo in repositories
    )
    total_forks = sum(
        repo.get("forks_count", 0) for repo in repositories
    )

    languages = Counter(
        repo["language"]
        for repo in repositories
        if repo.get("language")
    )

    print("\n" + "=" * 48)
    print("             DEVELOPER STATISTICS")
    print("=" * 48)
    print(f"Repositories analyzed : {total_repos}")
    print(f"Total stars           : {total_stars}")
    print(f"Total forks           : {total_forks}")

    print("\nProgramming Languages:")

    if languages:
        for language, count in languages.most_common():
            print(f"  {language}: {count} repositories")
    else:
        print("  Language data available nahi hai.")

    if repositories:
        top_repo = max(
            repositories,
            key=lambda repo: repo.get("stargazers_count", 0)
        )
        print("\nMost-starred repository:")
        print(f"  {top_repo.get('name', 'N/A')}")
        print(f"  Stars: {top_repo.get('stargazers_count', 0)}")

    print("=" * 48)


def main():
    print("\n" + "*" * 48)
    print("       GITHUB PROFILE ANALYZER")
    print("*" * 48)

    username = input("\nGitHub username enter karo: ").strip()

    if not username:
        print("Username khali nahi hona chahiye.")
        return

    profile = get_github_profile(username)

    if profile is None:
        print("Profile load nahi hui. Username check karo.")
        return

    repositories = get_repositories(username)
    show_statistics(repositories)


if __name__ == "__main__":
    main()