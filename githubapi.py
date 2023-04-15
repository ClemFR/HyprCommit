import datetime
import time

import requests
import config

last_reponse = None

def get_header():
    header = {}
    if config.get_gh_api_key() is not None:
        header = {"Authorization": f"Bearer {config.get_gh_api_key()}"}
    return header


def rate_limit(do_not_refresh=True):
    global last_reponse
    if last_reponse is None and not do_not_refresh:
        header = get_header()
        url = "https://api.github.com"
        last_reponse = requests.get(url, headers=header)

    if last_reponse is None:
        retour = "Pas de requête effectuée"
    else:
        retour = f"Token consommé : {last_reponse.headers['X-RateLimit-Used']} sur {last_reponse.headers['X-RateLimit-Limit']} | (restant : {last_reponse.headers['X-RateLimit-Remaining']})"
        reset_epoch = int(last_reponse.headers['X-RateLimit-Reset'])
        reset_time = time.strftime('%H:%M:%S', time.localtime(reset_epoch))
        remaining_time = datetime.timedelta(seconds=reset_epoch - time.time())
        retour += f"\nReset à : {reset_time} ({remaining_time} restant)"

    if get_header() != {}:
        retour += f"\nAuthentifié avec un token github"
    else:
        retour += f"\nNon authentifié, limite de base de l'api github"
    return retour, last_reponse is not None


def get_user_email(username: str) -> str | list[str]:
    global last_reponse
    """get the amil or a list of emails of a github user"""
    header = get_header()

    url = f"https://api.github.com/users/{username}"

    response = requests.get(url, headers=header)
    last_reponse = response

    if response.status_code == 200:
        print("User found!")

        if response.json()["email"] is not None:
            return response.json()["email"]
        else:
            print("User has no public email ! scrapping his repos...")

        repos = response.json()["repos_url"]
        response = requests.get(repos, headers=header)
        last_reponse = response

        if response.status_code == 200:
            reposjson = response.json()
            print(f"User has {len(reposjson)} public repos")

            repos_commits_url = []
            for repo in reposjson:
                if not repo["fork"]:
                    print(f"Repo {repo['name']} is not a fork, adding to list")
                    repos_commits_url.append(repo["commits_url"].replace("{/sha}", ""))

            print(f"User has {len(repos_commits_url)} repos with commits")

            if len(repos_commits_url) > 8:
                print("User has more than 8 repos with commits, cutting the list to 8 to limit api rate usage")
                repos_commits_url = repos_commits_url[:8]

            email_list = []
            for repo in repos_commits_url:
                response = requests.get(repo, headers=header)
                last_reponse = response
                if response.status_code == 200:
                    commits = response.json()
                    for commit in commits:
                        if commit["commit"]["author"]["name"] == username:
                            email = commit["commit"]["author"]["email"]
                            if email not in email_list:
                                email_list.append(email)
                                print(f"Email found: {email}")
                else:
                    print(f"Error while getting commits from repo {repo}")
                    print(f"Error code: {response.status_code}")
                    print(f"Error message: {response.text}")

            if len(email_list) == 0:
                print("No email found")
                return ""
            else:
                print(f"Email list: {email_list}")
                return email_list
