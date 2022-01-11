import os

from floxcore.config import Configuration, ParamDefinition


class GitHubConfiguration(Configuration):
    def parameters(self):
        return (
            ParamDefinition("organization", "GitHub default organization"),
            ParamDefinition("default_branch", "Default branch", default="develop"),
            ParamDefinition("vulnerability_alert", "Enable vulnerability alerts", default=True, boolean=True),
            ParamDefinition("automated_security_fixes", "Enable automated security fixes", default=True, boolean=True),
            ParamDefinition("protected_branches", "List of protected branches", default=["master"], multi=True),
            ParamDefinition("private", "Create repository as private", default=True, boolean=True),
            ParamDefinition("projects", "Enable projects", default=True, boolean=True),
            ParamDefinition("issues", "Enable issue management", default=True, boolean=True),
            ParamDefinition("wiki", "Enable wiki", default=True, boolean=True),
            ParamDefinition("collaborators_pull", 'Collaborators with "pull" permission', default=[], multi=True),
            ParamDefinition("collaborators_push", 'Collaborators with "push" permission', default=[], multi=True),
            ParamDefinition("collaborators_admin", 'Collaborators with "admin" permission', default=[], multi=True),
        )

    def secrets(self):
        return (
            ParamDefinition("token", "GitHub Access Token", secret=True, default=os.getenv("GITHUB_TOKEN")),
        )

    def schema(self):
        pass
