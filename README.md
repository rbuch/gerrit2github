# Migrating Gerrit to GitHub

1. Use `gerrit2github.py` to download Gerrit changesets and create branches on
   GitHub. See the file for information on the information that needs to be changed.

2. Edit `config.py` to add information about collaborators, GitHub API tokens, etc.

3. Run `make_prs.py` to create Pull Requests from the GitHub branches.
