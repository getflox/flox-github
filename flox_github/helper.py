from functools import wraps

from github import GithubException

from floxcore.exceptions import PluginException


def handle_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GithubException as e:
            if e.data:
                message = e.data.get("message")
                documentation = e.data.get("documentation_url", e.data.get("errors"))
                raise PluginException(f'[Github API] [{e.status}] "{message}" check "{documentation}".')
            else:
                raise PluginException(f"[Github API] [HTTP Status: {e.status}]")

    return wrapper


def authenticate_url(url: str, github_api):
    if "github.com" not in url or not url.startswith("https://"):
        return url

    return url.replace("https://", f"https://{github_api.flox.secrets.getone('github_token')}@")
