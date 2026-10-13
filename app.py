from flask import Flask, render_template, request
import requests
from collections import Counter

app = Flask(__name__)

API_URL = "https://api.github.com"


def get_github_data(username):
    try:
        response = requests.get(
            f"{API_URL}/users/{username}",
            timeout=10
        )

        if response.status_code == 404:
            return None, [], "GitHub username nahi mila."

        response.raise_for_status()
        profile = response.json()

        repos_response = requests.get(
            f"{API_URL}/users/{username}/repos",
            params={
                "sort": "updated",
                "per_page": 100,
                "page": 1
            },
            timeout=10
        )
        repos_response.raise_for_status()
        repositories = repos_response.json()

        if not isinstance(repositories, list):
            return None, [], "Repository data sahi nahi mila."

        return profile, repositories, None

    except requests.exceptions.Timeout:
        return None, [], "Request timeout. Dobara try karo."

    except requests.exceptions.RequestException:
        return None, [], "Internet ya GitHub API error. Dobara try karo."


@app.route("/", methods=["GET", "POST"])
def dashboard():
    profile = None
    repositories = []
    languages = {}
    total_stars = 0
    total_forks = 0
    error = None
    username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            error = "GitHub username enter karo."
        else:
            profile, repositories, error = get_github_data(username)

            if profile and not error:
                total_stars = sum(
                    repo.get("stargazers_count", 0)
                    for repo in repositories
                )

                total_forks = sum(
                    repo.get("forks_count", 0)
                    for repo in repositories
                )

                languages = dict(Counter(
                    repo["language"]
                    for repo in repositories
                    if repo.get("language")
                ).most_common())

                repositories.sort(
                    key=lambda repo: repo.get("stargazers_count", 0),
                    reverse=True
                )

    return render_template(
        "index.html",
        profile=profile,
        repositories=repositories[:20],
        languages=languages,
        total_stars=total_stars,
        total_forks=total_forks,
        error=error,
        username=username
    )


if __name__ == "__main__":
    app.run(debug=True)