# GitHub integration for flox

[flox](https://github.com/getflox/flox) automation for GitHub repository managmenet

## Exposed variables

- github_clone_url - http checkout URL 
- github_url - public URL of the repository 
- github_ssh_url - checkout URL used for git+ssh protocol
- github_repository - repository object as fetched from GitHub API 
- `github_empty` -  True/False flag
- `git_repository` - authenticated URL which can be used for all write operations

## Installation 

```bash
$ flox plugin install flox-github
```

or 

```bash
$ pip install flox-github
```


## Configuration 

```bash
$ flox config --plugin github --scope=user

ℹ Starting configuration of github for 'user' scope
 → GitHub default organization [getflox]:
 → Default branch [develop]:
 → Enable vulnerability alerts [Y/n]:
 → Enable automated security fixes [Y/n]:
ℹ 'List of protected branches' configuration is accepting multiple values, each in new line, enter empty value to end input, '-' to delete value
 → List of protected branches [master]:
 → Create repository as private [Y/n]:
 → Enable projects [Y/n]:
 → Enable issue management [Y/n]:
 → Enable wiki [Y/n]:
ℹ 'Collaborators with "pull" permission' configuration is accepting multiple values, each in new line, enter empty value to end input, '-' to delete value
ℹ 'Collaborators with "push" permission' configuration is accepting multiple values, each in new line, enter empty value to end input, '-' to delete value
ℹ 'Collaborators with "admin" permission' configuration is accepting multiple values, each in new line, enter empty value to end input, '-' to delete value

New configuration:

 Key                                    Old value  New value
─────────────────────────────────────────────────────────────
 Collaborators with "pull" permission   {}         -
 Collaborators with "push" permission   {}         -
 Collaborators with "admin" permission  {}         -

Save plugin settings? [y/N]: y
ℹ Configuration saved: /Users/user/.flox/settings.toml
 → GitHub Access Token [xxx]: ------
 
New configuration:

 Key                  Old value                                  New value
──────────────────────────────────────────────────────────────────────────────────────────────────────────
 GitHub Access Token  -----                                      --------

Save plugin settings? [y/N]: y
ℹ Updated 1 secrets
```
