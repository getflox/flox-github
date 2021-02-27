from flox_github.remote import with_github
from floxcore.context import Flox


@with_github
def docker_credentials_provider(flox: Flox, repository: str, github_api, **kwargs):
    if repository != "docker.pkg.github.com":
        return None

    return github_api.context.login, flox.secrets.getone("github_token"), repository
