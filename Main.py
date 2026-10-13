import requests
from collections import Counter

API_URL = "https://api.github.com"


def fetch_data(url, params=None):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
            headers={"Accept": "application/vnd.github+json"}
        )

        if response.status_code == 404:
            print("GitHub user nahi mila.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Request timeout. Dobara try karo.")
    except requests.exceptions.RequestException as error:
        print("API error:", error)

    return None


def get_profile(username):
    profile = fetch_data(f"{API_URL}/users/{username}")

    if not profile:
        return None

    print("\n" + "=" * 45)
    print("        GITHUB PROFILE ANALYZER")
    print("=" * 45)
    print(f"Username     : {profile.get('login')}")
    print(f"Name         : {profile.get('name') or 'Not provided'}")
    print(f"Bio          : {profile.get('bio') or 'Not provided'}")
    print(f"Followers    : {profile.get('followers', 0)}")
    print(f"Following    : {profile.get('following', 0)}")
    print(f"Public repos : {profile.get('public_repos', 0)}")
    print(f"Profile URL  : {profile.get('html_url')}")
    print("=" * 45)

    return profile


def get_repositories(username):
    repositories = []
    page = 1

    while page <= 10:
        data = fetch_data(
            f"{API_URL}/users/{username}/repos",
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page
            }
        )

        if data is None:
            return None

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def show_statistics(repositories):
    if repositories is None:
        print("Repository data load nahi hui.")
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

    print("\n" + "=" * 45)
    print("           DEVELOPER STATISTICS")
    print("=" * 45)
    print(f"Repositories : {len(repositories)}")
    print(f"Total stars  : {total_stars}")
    print(f"Total forks  : {total_forks}")

    print("\nProgramming Languages:")
    if languages:
        for language, count in languages.most_common():
            print(f"  {language}: {count} repositories")
    else:
        print("  Language data available nahi hai.")

    top_repos = sorted(
        repositories,
        key=lambda repo: repo.get("stargazers_count", 0),
        reverse=True
    )

    print("\nTop 5 Repositories:")
    for repo in top_repos[:5]:
        print(
            f"  {repo['name']} | "
            f"Stars: {repo.get('stargazers_count', 0)} | "
            f"Forks: {repo.get('forks_count', 0)}"
        )
        print(f"  {repo.get('html_url', '')}")

    print("=" * 45)


def search_repositories(repositories):
    if repositories is None:
        return

    keyword = input(
        "\nRepository search keyword enter karo: "
    ).strip().lower()

    if not keyword:
        print("Search keyword empty hai.")
        return

    matches = [
        repo for repo in repositories
        if keyword in repo.get("name", "").lower()
        or keyword in (repo.get("description") or "").lower()
    ]

    print(f"\nSearch results: {len(matches)}")

    for repo in matches:
        print(
            f"- {repo['name']} "
            f"(Stars: {repo.get('stargazers_count', 0)})"
        )
        print(f"  {repo.get('html_url', '')}")


def main():
    print("Welcome to GitHub Profile Analyzer!")

    username = input("GitHub username: ").strip()

    if not username:
        print("Username enter karna zaroori hai.")
        return

    profile = get_profile(username)

    if profile is None:
        print("Profile load nahi hui. Username check karo.")
        return

    repositories = get_repositories(username)

    if repositories is None:
        return

    show_statistics(repositories)

    while True:
        print("\nMENU")
        print("1. Search repositories")
        print("2. Show statistics again")
        print("3. Exit")

        choice = input("Option choose karo: ").strip()

        if choice == "1":
            search_repositories(repositories)
        elif choice == "2":
            show_statistics(repositories)
        elif choice == "3":
            print("Thank you for using GitHub Profile Analyzer!")
            break
        else:
            print("Invalid option. 1, 2 ya 3 choose karo.")


if __name__ == "__main__":
    main()