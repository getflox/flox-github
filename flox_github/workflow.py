from flox_github.helper import handle_exceptions
from flox_github.remote import with_github
from floxcore.context import Flox


@handle_exceptions
@with_github
def create_pr(flox: Flox, out, github_api, flow_id, description, **kwargs):
    """Create Pull Request"""
    repository = github_api.get_repository(flox.id)
    pulls = repository.get_pulls(head=f"{github_api.context.login}:{flow_id}", state='open')
    if pulls.totalCount > 0:
        pr = pulls[0]
        out.info(f"Using existing Pull Request {pr.html_url}")
    else:
        pr = repository.create_pull(
            title=f"[WIP] {description}",
            body="",
            head=flow_id,
            base=repository.default_branch,
        )
        out.success(f"Created new Pull Request {pr.html_url}")

    return dict(github_pr_url=pr.html_url)


@handle_exceptions
@with_github
def update_pr(flox: Flox, out, github_api, flow_id, description, **kwargs):
    """Update Pull Request"""
    repository = github_api.get_repository(flox.id)
    pulls = repository.get_pulls(head=flow_id, state='open')
    if pulls.totalCount == 0:
        out.warning(f"Unable to located related PR")
        return

    pulls[0].edit(title=pulls[0].title.replace("[WIP] ", ""))
    out.success("Removed [WIP] flag")
