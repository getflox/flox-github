from floxcore.context import Flox
from floxcore.utils.string import as_flag

from flox_github.helper import handle_exceptions, authenticate_url
from flox_github.remote import with_github, UnifiedApi


@handle_exceptions
@with_github
def dump_variables(flox: Flox, github_api: UnifiedApi, out, **kwargs):
    repo = github_api.get_repository(flox.id)

    return dict(
        github_clone_url=repo.clone_url,
        github_url=repo.html_url,
        github_ssh_url=repo.ssh_url,
        github_repository=repo,
        github_empty=repo.get_commits().totalCount == 0,
        git_repository=authenticate_url(repo.clone_url, github_api),
        git_remote_has_branches=repo.get_branches().totalCount > 0,
        git_default_branch=repo.default_branch
    )


@handle_exceptions
@with_github
def create_repository(flox: Flox, github_api: UnifiedApi, out, **kwargs):
    """Create GitHub repository"""
    repo = github_api.get_repository(flox.id)
    if repo:
        out.info(f"Skipping existing GitHub repository '{flox.id}'")
    else:
        configuration = dict(
            private=bool(flox.settings.github.private),
            has_projects=bool(flox.settings.github.projects),
            auto_init=True,
            has_issues=bool(flox.settings.github.issues),
            has_wiki=bool(flox.settings.github.wiki)
        )

        repo = github_api.create_repository(flox.id, **configuration)
        out.success(f"Created GitHub repository '{repo.html_url}'")


@handle_exceptions
@with_github
def configure_repository(flox, github_api, github_repository, out, **kwargs):
    """Configure GitHub repository"""
    if flox.settings.github.vulnerability_alert:
        if not github_repository.get_vulnerability_alert():
            github_repository.enable_vulnerability_alert()
            out.success("Vulnerability alerts enabled")
    else:
        github_repository.disable_vulnerability_alert()
        out.warning("Vulnerability alerts disabled")

    out.success(f"Vulnerability alerts: {as_flag(flox.settings.github.automated_security_fixes)}")

    if flox.settings.github.automated_security_fixes:
        github_repository.enable_automated_security_fixes()
        out.success(f"Automated security fixes enabled")
    else:
        out.warn(f"Automated security fixes disabled")

    protection_rule = {"required_approving_review_count": 2}

    for branch_name in flox.settings.github.protected_branches or []:
        branch = github_api.get_branch(github_repository, branch_name)

        if branch.protected:
            out.info(f'Branch "{branch_name}" has protection rules set.')

        branch.edit_protection(**protection_rule)
        out.success(f'Branch protection rules set for "{branch_name}" branch.')

    github_collaborators = [c.login for c in github_repository.get_collaborators()]
    flox_collaborators = []
    for permission in ("pull", "push", "admin"):
        collaborators = list(filter(None, getattr(flox.settings.github, f"collaborators_{permission}")))
        if collaborators:
            flox_collaborators.extend(
                [{"name": u, "perm": permission} for u in getattr(flox.settings.github, f"collaborators_{permission}")])

    for collaborator in flox_collaborators:
        if collaborator not in github_collaborators:
            github_repository.add_to_collaborators(collaborator["name"], collaborator["perm"])
            out.success(f'Collaborator "{collaborator["name"]}" added')
        else:
            out.info(f'Collaborator "{collaborator["name"]}" already added')
