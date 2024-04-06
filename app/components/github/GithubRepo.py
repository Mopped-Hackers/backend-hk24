import os
from git import Repo


def extract_repo_name_from_url(url):
    # Splitting the URL into parts
    parts = url.split("/")

    # The repository name is usually after the domain name (github.com) and the username
    # So, it's typically the 5th element in the list if the URL starts with http:// or https://
    # Checking if the URL starts with 'http' to accommodate both 'http' and 'https'
    if url.startswith("http://") or url.startswith("https://"):
        return parts[4]  # Returning the repository name part
    else:
        return parts[2]  # This handles URLs that start directly with 'github.com'


def download_repo(url: str, targetDir: str) -> bool:
    try:
        Repo.clone_from(url, os.path.join(targetDir, extract_repo_name_from_url(url)))
    except:
        return False

    return True
