#!/usr/bin/python3
"""Deploy a web_static archive to the configured web servers."""

import os

from fabric.api import env, put, run, settings


env.hosts = ["184.73.19.238", "35.175.218.108"]


def _run(command):
    """Run a remote command and report whether it succeeded."""
    result = run(command)
    return not result.failed


def do_deploy(archive_path):
    """Deploy an archive and switch the current release symlink."""
    if not os.path.isfile(archive_path):
        return False

    archive_name = os.path.basename(archive_path)
    if not archive_name.endswith(".tgz"):
        return False
    release_name = archive_name[:-4]
    release_path = "/data/web_static/releases/{}".format(release_name)

    with settings(warn_only=True):
        uploaded = put(archive_path, "/tmp/{}".format(archive_name))
        if uploaded.failed:
            return False
        if not _run("mkdir -p {}".format(release_path)):
            return False
        if not _run(
            "tar -xzf /tmp/{0} -C {1}".format(archive_name, release_path)
        ):
            return False
        if not _run("rm -f /tmp/{}".format(archive_name)):
            return False
        if not _run("rm -f /data/web_static/current"):
            return False
        if not _run(
            "if [ -d {0}/web_static ]; then "
            "ln -s {0}/web_static /data/web_static/current; "
            "else ln -s {0} /data/web_static/current; fi".format(
                release_path
            )
        ):
            return False

    return True
