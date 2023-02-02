import inspect
from functools import wraps
from os import getenv

import github
import click
from github import Github, UnknownObjectException, GithubException, Consts
from github.Repository import Repository

from floxcore.exceptions import PluginException


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


class GitHubException(PluginException):
    """Problems with Github"""


class UnifiedApi:
    """
    Unified API class - hiding differences between organisation and user
    """

    def __init__(self, flox, github, organization=None, github_user_owned=None, **kwargs):
        if not flox:
            raise GitHubException("Unable to create UnifiedApi instance, flox instance is required")

        self.org = organization or flox.profile.github.get("organization")
        if not self.org and not github_user_owned:
            self.org = flox.profile.github.organization = click.prompt("\nGitHub organization name")

        self.flox = flox
        self.github = github

        if github_user_owned:
            self.context = github.get_user()
        else:
            self.context = github.get_organization(self.org)

    def create_repository(
            self,
            name,
            description=github.GithubObject.NotSet,
            homepage=github.GithubObject.NotSet,
            private=github.GithubObject.NotSet,
            visibility=github.GithubObject.NotSet,
            has_issues=github.GithubObject.NotSet,
            has_wiki=github.GithubObject.NotSet,
            has_downloads=github.GithubObject.NotSet,
            has_projects=github.GithubObject.NotSet,
            team_id=github.GithubObject.NotSet,
            auto_init=github.GithubObject.NotSet,
            license_template=github.GithubObject.NotSet,
            gitignore_template=github.GithubObject.NotSet,
            allow_squash_merge=github.GithubObject.NotSet,
            allow_merge_commit=github.GithubObject.NotSet,
            allow_rebase_merge=github.GithubObject.NotSet,
            delete_branch_on_merge=github.GithubObject.NotSet,
            **kwargs
    ):
        assert isinstance(name, str), name
        assert description is github.GithubObject.NotSet or isinstance(description, str), description
        assert homepage is github.GithubObject.NotSet or isinstance(homepage, str), homepage
        assert private is github.GithubObject.NotSet or isinstance(private, bool), private
        assert visibility is github.GithubObject.NotSet or isinstance(visibility, str), visibility
        assert has_issues is github.GithubObject.NotSet or isinstance(has_issues, bool), has_issues
        assert has_wiki is github.GithubObject.NotSet or isinstance(has_wiki, bool), has_wiki
        assert has_downloads is github.GithubObject.NotSet or isinstance(has_downloads, bool), has_downloads
        assert has_projects is github.GithubObject.NotSet or isinstance(has_projects, bool), has_projects
        assert team_id is github.GithubObject.NotSet or isinstance(team_id, int), team_id
        assert auto_init is github.GithubObject.NotSet or isinstance(auto_init, bool), auto_init
        assert license_template is github.GithubObject.NotSet or isinstance(license_template, str), license_template
        assert gitignore_template is github.GithubObject.NotSet or isinstance(
            gitignore_template, str
        ), gitignore_template
        assert allow_squash_merge is github.GithubObject.NotSet or isinstance(
            allow_squash_merge, bool
        ), allow_squash_merge
        assert allow_merge_commit is github.GithubObject.NotSet or isinstance(
            allow_merge_commit, bool
        ), allow_merge_commit
        assert allow_rebase_merge is github.GithubObject.NotSet or isinstance(
            allow_rebase_merge, bool
        ), allow_rebase_merge
        assert delete_branch_on_merge is github.GithubObject.NotSet or isinstance(
            delete_branch_on_merge, bool
        ), delete_branch_on_merge
        post_parameters = {
            "name": name,
        }
        if description is not github.GithubObject.NotSet:
            post_parameters["description"] = description
        if homepage is not github.GithubObject.NotSet:
            post_parameters["homepage"] = homepage
        if private is not github.GithubObject.NotSet:
            post_parameters["private"] = private
        if visibility is not github.GithubObject.NotSet:
            post_parameters["visibility"] = visibility
        if has_issues is not github.GithubObject.NotSet:
            post_parameters["has_issues"] = has_issues
        if has_wiki is not github.GithubObject.NotSet:
            post_parameters["has_wiki"] = has_wiki
        if has_downloads is not github.GithubObject.NotSet:
            post_parameters["has_downloads"] = has_downloads
        if has_projects is not github.GithubObject.NotSet:
            post_parameters["has_projects"] = has_projects
        if team_id is not github.GithubObject.NotSet:
            post_parameters["team_id"] = team_id
        if auto_init is not github.GithubObject.NotSet:
            post_parameters["auto_init"] = auto_init
        if license_template is not github.GithubObject.NotSet:
            post_parameters["license_template"] = license_template
        if gitignore_template is not github.GithubObject.NotSet:
            post_parameters["gitignore_template"] = gitignore_template
        if allow_squash_merge is not github.GithubObject.NotSet:
            post_parameters["allow_squash_merge"] = allow_squash_merge
        if allow_merge_commit is not github.GithubObject.NotSet:
            post_parameters["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not github.GithubObject.NotSet:
            post_parameters["allow_rebase_merge"] = allow_rebase_merge
        if delete_branch_on_merge is not github.GithubObject.NotSet:
            post_parameters["delete_branch_on_merge"] = delete_branch_on_merge

        post_parameters.update(**kwargs)

        headers, data = self.context._requester.requestJsonAndCheck(
            "POST",
            f"{self.context.url}/repos",
            input=post_parameters,
            headers={"Accept": Consts.repoVisibilityPreview},
        )

        return github.Repository.Repository(self.context._requester, headers, data, completed=True)

    def get_repository(self, name) -> Repository:
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
        token = getenv("GITHUB_TOKEN")

        if not hasattr(with_github, "client"):
            with_github.client = Github(token)

        sig = inspect.signature(f)

        if "github" in sig.parameters:
            kwargs["github"] = with_github.client

        if "github_api" in sig.parameters:
            if not hasattr(with_github, "api"):
                with_github.api = UnifiedApi(github=with_github.client, **kwargs)

            kwargs["github_api"] = with_github.api
            kwargs.setdefault("organization", with_github.api.org)

        if "github_token" in sig.parameters:
            kwargs["github_token"] = token

        return f(*args, **kwargs)

    return wrapper
