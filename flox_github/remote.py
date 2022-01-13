import inspect
from functools import wraps

from click import ClickException
from github import Github, UnknownObjectException, GithubException
from github.Repository import Repository


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


class GitHubException(ClickException):
    """Problems with Github"""


class UnifiedApi:
    """
    Unified API class - hiding differences between organisation and user
    """

    def __init__(self, flox, github, github_org=None, github_user_owned=None, **kwargs):
        if not flox:
            raise GitHubException("Unable to create UnifiedApi instance, flox instance is required")

        self.org = github_org or flox.settings.github.organization
        if not self.org and not github_user_owned:
            raise GitHubException("You need to specify GitHub organisation before using flox-github.")

        self.flox = flox
        self.github = github

        if github_user_owned:
            self.context = github.get_user()
        else:
            self.context = github.get_organization(self.org)

    def create_repository(self, name, **kwargs):
        return self.context.create_repo(name, **kwargs)

    def get_repository(self, name):
        try:
            return self.context.get_repo(name)
        except UnknownObjectException:
            return None

    def get_branch(self, repository, branch):
        if not isinstance(repository, Repository):
            repository = self.context.get_repo(repository)

        try:
            return repository.get_branch(branch)
        except GithubException:
            return None

    @require_admin
    def create_branch(self, repository, branch):
        if not isinstance(repository, Repository):
            repository = self.context.get_repo(repository)

        master_branch = repository.get_branch("master")

        return repository.create_git_ref(ref=f"refs/heads/{branch}", sha=master_branch.commit.sha)


def with_github(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        flox = kwargs.get("flox")
        token = flox.secrets.getone("github_token", required=True)

        if not hasattr(with_github, "client"):
            with_github.client = Github(token)

        sig = inspect.signature(f)

        if 'github' in sig.parameters:
            kwargs['github'] = with_github.client

        if 'github_api' in sig.parameters:
            if not hasattr(with_github, "api"):
                with_github.api = UnifiedApi(github=with_github.client, **kwargs)

            kwargs['github_api'] = with_github.api

        if 'github_token' in sig.parameters:
            kwargs['github_token'] = token

        return f(*args, **kwargs)

    return wrapper
