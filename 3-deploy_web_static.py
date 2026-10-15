#!/usr/bin/python3
"""Pack and deploy the web_static directory."""

from fabric.api import env

env.hosts = ["44.212.60.247", "3.82.250.215"]

pack = __import__("1-pack_web_static")
deployer = __import__("2-do_deploy_web_static")


def deploy():
    """Create and distribute an archive to both web servers."""
    archive_path = pack.do_pack()
    if archive_path is None:
        return False
    return deployer.do_deploy(archive_path)
