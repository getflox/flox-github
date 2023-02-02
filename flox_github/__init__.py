from flox_github.project import create_repository, configure_access, configure_branches, dump_variables

from floxcore import Plugin


class GitHubPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__(help="Work effectively with GitHub repositories")

        self.project_stages.add(callback=create_repository, priority=1000)
        self.project_stages.add(callback=configure_access, priority=2000)
        self.project_stages.add(callback=configure_branches, priority=2000)


plugin = GitHubPlugin()
