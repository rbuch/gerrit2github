#!/usr/bin/env python3

import json
import os
import requests
import sys
import time
import re

from config import *
import config


def make_request(_url, _user, _data=None, _type='GET', _headers={}):
    _headers['Authorization'] = 'token {0}'.format(get_github_token(_user))

    url = 'https://api.github.com/repos/{0}'.format(GITHUB_REPO) + _url

    time.sleep(2)
    response = requests.request(_type, url, data=_data, headers=_headers)

    return response


def make_pr(title, body, head, base, user, date):
    # Create a PR on github.com using the given parameters

    realuser = get_github_username(user)

    orig_pr_num = head.split('/')[2]

    body = '*Original PR: https://charm.cs.illinois.edu/gerrit/{0}'.format(orig_pr_num) + "*\n\n---\n" + body

    body = '*Original date: {0}*\n'.format(date) + body

    if not gerrit_user_has_token(user):
        if gerrit_user_has_github_name(user):
            body = "*Original author: " + user + " (@" + github_usermap[user] + ")*\n" + body
        else:
            body = "*Original author: " + user + "*\n" + body


    data = {'title': title,
            'body': body,
            'head': head,
            'base': base,
            'maintainer_can_modify': True,
           }

    payload = json.dumps(data)

    response = make_request('/pulls', realuser, _data=payload, _type="POST")

    if response.status_code != 201:
        print('Could not create pull request: title:"{0}", user: {1}, realuser: {2}, payload: {3}'.format(title,user,realuser,payload))
        print('Response:', response.content)
        sys.exit(1)
    else:
        data = json.loads(response.text)
        myurl = data['html_url']

        if "X-RateLimit-Remaining" in response.headers: 
            print('  PR: "{0}" {1} ({2})'.format(title.split('\n')[0][:40], myurl, response.headers["X-RateLimit-Remaining"]))
        else:
            print('  PR: "{0}" {1}'.format(title.split('\n')[0][:40]), myurl)


def gerrit_user_has_token(gerrit_user):
    if gerrit_user in github_usermap:
        github_user = github_usermap[gerrit_user]
        if github_user in github_tokenmap:
            return True
    return False

def gerrit_user_has_github_name(gerrit_user):
    if gerrit_user in github_usermap:
            return True
    return False

unknown_github_username = set()
unknown_github_token = set()

def get_github_username(gerrit_user):
    if gerrit_user in github_usermap:
        return(github_usermap[gerrit_user])
    else:
        if gerrit_user not in unknown_github_username:
            print('  Gerrit user "{0}" not in github_usermap, using default GitHub user "{1}".'.format(gerrit_user, github_default_username))
            unknown_github_username.add(gerrit_user)
        return(github_default_username)


def get_github_token(github_user):
    if github_user in github_tokenmap:
        return(github_tokenmap[github_user])
    else:
        if github_user not in unknown_github_token:
            print('  GitHub user "{0}" not in github_tokenmap, using token for default GitHub user "{1}".'.format(github_user, github_default_username))
            unknown_github_token.add(github_user)
        return(github_tokenmap[github_default_username])


def list_branches():
    res = []
    response = make_request('/branches?per_page=100', github_default_username)

    data = json.loads(response.text)

    for k in data:
        name = k['name']
        if name.startswith('review/'):
            res.append(name)

    while 'next' in response.links:
        response = requests.get(response.links['next']['url'])

        data = json.loads(response.text)

        for k in data:
            name = k['name']
            if name.startswith('review/'):
                res.append(name)


    return res

def get_branch_data(branch):
    response = make_request('/git/refs/heads/{0}'.format(branch), github_default_username)

    data = json.loads(response.text)

    commit = data['object']['sha']

    response = make_request('/git/commits/{0}'.format(commit), github_default_username)

    data = json.loads(response.text)

    author = data['committer']['name']
    text = data['message'].splitlines()

    date = data['committer']['date'].replace("T", " ").replace("Z", "")

    title = text[0]
    body = '\n'.join(text[1:])

    return(author, title, body, date)


print('=' * 80)

branches = list_branches()
# branches = [ "review/yan_ming_li/761" ]

print('Creating {0} pull requests in GitHub repository "{1}".'.format(len(branches), GITHUB_REPO))
print('=' * 80)

for branch in branches:
    author, title, body, date = get_branch_data(branch)
    make_pr(title, body, branch, 'master', author, date)

print('=' * 80)
print('Finished.')

if len(unknown_github_username) > 0:
    print('The following Gerrit users did not have a GitHub username associated with them:')
    print(unknown_github_username)

if len(unknown_github_token) > 0:
    print('The following GitHub users did not have a GitHub token associated with them:')
    print(unknown_github_token)
