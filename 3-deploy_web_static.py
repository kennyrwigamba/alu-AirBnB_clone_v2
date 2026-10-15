#!/usr/bin/python3
"""Pack and deploy the web_static directory."""

import os
from datetime import datetime
from shlex import quote

from fabric.api import env, local, put, run, settings


env.hosts = ["44.212.60.247", "3.82.250.215"]
env.user = "ubuntu"


def do_pack():
    """Generate a timestamped archive, returning None when packing fails."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(timestamp)
    try:
        with settings(warn_only=True):
            if local("mkdir -p versions", capture=True).failed:
                return None
            if local("tar -czf {} web_static".format(quote(archive_path)),
                     capture=True).failed:
                return None
    except (Exception, SystemExit):
        return None
    return archive_path


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
    if release_name in ("", ".", ".."):
        return False
    release_path = "/data/web_static/releases/{}".format(release_name)
    remote_archive = "/tmp/{}".format(archive_name)
    nested_path = release_path + "/web_static"

    commands = (
        "mkdir -p {}".format(quote(release_path)),
        "tar -xzf {} -C {}".format(quote(remote_archive), quote(release_path)),
        "rm -f {}".format(quote(remote_archive)),
        "if [ -d {0} ]; then cp -a {1} {2} && rm -rf {0}; fi".format(
            quote(nested_path), quote(nested_path + "/."),
            quote(release_path + "/"),
        ),
        "rm -f /data/web_static/current",
        "ln -s {} /data/web_static/current".format(quote(release_path)),
    )

    try:
        with settings(warn_only=True):
            if put(archive_path, remote_archive).failed:
                return False
            for command in commands:
                if not _run(command):
                    return False
    except (Exception, SystemExit):
        return False

    print("New version deployed!")
    return True


def deploy():
    """Create and distribute an archive to both web servers."""
    archive_path = do_pack()
    if not archive_path:
        return False
    return do_deploy(archive_path)
