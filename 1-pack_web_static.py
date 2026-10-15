#!/usr/bin/python3
"""Create a compressed archive of the web_static directory."""

from datetime import datetime

from fabric.api import local


def do_pack():
    """Generate and return a timestamped web_static archive path."""
    versions = local("mkdir -p versions", capture=True)
    if versions.failed:
        return None

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(timestamp)
    archive = local(
        "tar -czf {} web_static".format(archive_path),
        capture=True,
    )
    if archive.failed:
        return None
    return archive_path
