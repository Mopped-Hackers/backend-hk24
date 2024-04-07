import os
from git import Repo
import shutil


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


def download_repo(url: str) -> str:

    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uploads_repo_folder = os.path.join(root_path, 'uploads/repos')
    if not os.path.exists(uploads_repo_folder):
        os.makedirs(uploads_repo_folder)
        
        
    path = os.path.join(uploads_repo_folder, extract_repo_name_from_url(url))

    if os.path.exists(path):
        shutil.rmtree(path)

    try:
        Repo.clone_from(url, path)
    except:
        raise Exception

    return path

def remove_repo(url: str) -> None:
    
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uploads_repo_folder = os.path.join(root_path, 'uploads/repos')
    if not os.path.exists(uploads_repo_folder):
        os.makedirs(uploads_repo_folder)
    path = os.path.join(uploads_repo_folder, extract_repo_name_from_url(url))
    if os.path.exists(path):
        shutil.rmtree(path)
