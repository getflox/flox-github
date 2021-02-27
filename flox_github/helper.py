from functools import wraps

from github import GithubException

from floxcore.exceptions import PluginException


def handle_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GithubException as e:
            message = e.data.get("message")
            documentation = e.data.get("documentation_url")
            raise PluginException(f'[Github API] [{e.status}] "{message}" check "{documentation}".')

    return wrapper


def authenticate_url(url: str, github_api):
    if 'github.com' not in url or not url.startswith("https://"):
        return url
    return url.replace("https://", f"https://{github_api.flox.secrets.getone('github_token')}@")
