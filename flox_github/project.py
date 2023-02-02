# from floxcore.context import Flox
# from floxcore.utils.string import as_flag
from github import Repository
from flox_github.helper import handle_exceptions, authenticate_url
from flox_github.remote import with_github, UnifiedApi
from floxcore import FloxContext


@handle_exceptions
@with_github
def dump_variables(flox: FloxContext, github_api: UnifiedApi, out, **kwargs):
    repo = github_api.get_repository(flox.project.id)

    return dict(
        github_clone_url=repo.clone_url,
        github_url=repo.html_url,
        github_ssh_url=repo.ssh_url,
        github_repository=repo,
        github_empty=repo.get_commits().totalCount == 0,
        git_repository=authenticate_url(repo.clone_url, github_api),
        git_remote_has_branches=repo.get_branches().totalCount > 0,
        git_default_branch=repo.default_branch,
    )


@handle_exceptions
@with_github
def create_repository(flox: FloxContext, github_api: UnifiedApi, output, organization, repository=None, **kwargs):
    """Create GitHub repository"""
    repo = github_api.get_repository(flox.project.id)
    repository.setdefault("name", flox.project.id)
    repository.setdefault("description", flox.project.description)
    repository.setdefault("auto_init", True)

    if repo:
        output.info(f"Applying repository settings '{organization}/{flox.project.id}'")
        update = {}
        for k, v in repository.items():
            if getattr(repo, k, None) != v:
                update[k] = v

        headers, data = repo._requester.requestJsonAndCheck(
            "PATCH", repo.url, input=update
        )
        repo._useAttributes(data)
    else:
        repo = github_api.create_repository(**repository)
        output.success(f"Created GitHub repository '{repo.html_url}'")

    return dict(
        git_repository=repo.clone_url,
        git_remote_has_branches=repo.get_branches().totalCount > 0,
        github_repository_name=repo.full_name,
    )


@handle_exceptions
@with_github
def configure_branches(flox: FloxContext, github_api: UnifiedApi, repository, workflow, output, **kwargs):
    """Configure branches"""
    repository.setdefault("name", flox.project.id)

    repo: Repository = github_api.get_repository(repository.get("name"))
    if repo:
        default_branch = github_api.get_branch(flox.project.id, repo.default_branch)

    main_branch = github_api.get_branch(flox.project.id, flox.profile.git.default_branch)
    if not main_branch:
        pass

    for branch in flox.profile.git.branches:
        pass

    for branch_name, required_approvals in (workflow.protection or {}).items():
        branch = github_api.get_branch(flox.project.id, branch_name)

        if not branch:
            # print("xxx")
            pass
        else:
            if branch.protected:
                output.info(f'Branch "{branch_name}" has protection rules set.')

            branch.edit_protection(required_approving_review_count=required_approvals)

        output.success(f'Branch protection rules set for "{branch_name}" branch.')


@handle_exceptions
@with_github
def configure_access(flox, github_api, output, **kwargs):
    """Configure GitHub Access"""

    #
    # github_collaborators = [c.login for c in github_repository.get_collaborators()]
    # flox_collaborators = []
    # for permission in ("pull", "push", "admin"):
    #     collaborators = list(filter(None, getattr(flox.settings.github, f"collaborators_{permission}")))
    #     if collaborators:
    #         flox_collaborators.extend(
    #             [{"name": u, "perm": permission} for u in getattr(flox.settings.github, f"collaborators_{permission}")])
    #
    # for collaborator in flox_collaborators:
    #     if collaborator not in github_collaborators:
    #         github_repository.add_to_collaborators(collaborator["name"], collaborator["perm"])
    #         out.success(f'Collaborator "{collaborator["name"]}" added')
    #     else:
    #         out.info(f'Collaborator "{collaborator["name"]}" already added')
