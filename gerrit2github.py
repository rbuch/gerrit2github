#! /usr/bin/env python

# Gerrit is assumed to be accessible via the charmgit ssh alias and be set as the "origin" remote
# Github is assumed to be set as the "github" remote
# Should be run somewhere inside the project folder (so the git commands work)

import sys
import os
import subprocess
import json
import re

def run_command_status(*argv, **kwargs):
    if len(argv) == 1:
        # for python2 compatibility with shlex
        if sys.version_info < (3,) and isinstance(argv[0], unicode):
            argv = shlex.split(argv[0].encode('utf-8'))
        else:
            argv = shlex.split(str(argv[0]))
    stdin = kwargs.pop('stdin', None)
    newenv = os.environ.copy()
    newenv['LANG'] = 'C'
    newenv['LANGUAGE'] = 'C'
    newenv.update(kwargs)
    p = subprocess.Popen(argv,
                         stdin=subprocess.PIPE if stdin else None,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         env=newenv, universal_newlines=True)
    (out, nothing) = p.communicate(stdin)
    return (p.returncode, out.strip())

def parseGerritChangesJSON(data):
    changes = []
    for line in data.split("\n"):
        if line[0] == "{":
            try:
                data = json.loads(line)
                if "type" not in data:
                    changes.append(data)
            except Exception:
                print "Error parsing Gerrit change requests", line
                sys.exit(-1)
    return changes

if len(sys.argv) < 2:
    print "Must specify project name"
    sys.exit(1)

project_name = sys.argv[1]


query = "project:%s status:open" % project_name
(returnValue, output) = run_command_status("ssh", "-x", "charmgit", 
                                               "gerrit", "query",
                                               "--format=JSON %s" % query)
changes = parseGerritChangesJSON(output)
print project_name, len(changes), "changes"

# Fetch the change requests from Gerrit and push them to Github
for change in changes:
    author = re.sub('\W+', '_', change['owner']['name']).lower()
    branchName = "review/%s/%s" % (author, change['number'])
    (returnValue, output) = run_command_status("ssh", "-x", "charmgit",
                                                   "gerrit", "query",
                                                   "--format=JSON", "--current-patch-set",
                                                   "change:%s" % change['number'])
    changeInfo = parseGerritChangesJSON(output)
    print branchName, changeInfo[0]["currentPatchSet"]["ref"]
    run_command_status("git", "fetch", "origin", changeInfo[0]["currentPatchSet"]["ref"])
    run_command_status("git", "checkout", "-b", branchName, "FETCH_HEAD")
    run_command_status("git", "push", "github", branchName)
