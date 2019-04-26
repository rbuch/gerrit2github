####################################################
# This file contains the user configuration.       #
# You will need to change the values in this file. #
####################################################

#
# GitHub API information
#

# The GitHub repository to add this issue to:
GITHUB_REPO = 'github_repo'

# Issues and comments will be assigned to this GitHub user if the real user is not
# in the map below
github_default_username = 'github_default_username'

# Maps Github user names to their Github access tokens. The tokens can be
# generated in Settings -> Developer Settings -> Personal access tokens,
# Generate new token. Only the public_repo scope is necessary.
github_tokenmap = {
  'github_user':  'github_token',
}

# Maps Gerrit user names to Github user names:
github_usermap = {
  'Gerrit user':  'github_user',
}
