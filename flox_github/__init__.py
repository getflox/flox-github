from flox_github.configure import GitHubConfiguration
from flox_github.docker import docker_credentials_provider
from flox_github.project import create_repository, configure_repository, dump_variables
from flox_github.workflow import create_pr, update_pr
from floxcore.command import Stage
from floxcore.context import Flox
from floxcore.plugin import Plugin


class GitHubPlugin(Plugin):
    def configuration(self):
        return GitHubConfiguration()

    def handle_variables(self, flox: Flox):
        return (
            Stage(dump_variables, priority=2000),
        )

    def handle_project(self, flox: Flox):
        return (
            Stage(create_repository, priority=2000),
            Stage(dump_variables, priority=2000),
            Stage(configure_repository, priority=200),
        )

    def handle_workflow_publish(self, flox: Flox):
        return (
            Stage(create_pr),
        )

    def handle_workflow_finish(self, flox: Flox):
        return (
            Stage(update_pr),
        )

    def handle_docker_credentials(self, flox: Flox, repository=None):
        return docker_credentials_provider(flox=flox, repository=repository)


def plugin():
    return GitHubPlugin()
