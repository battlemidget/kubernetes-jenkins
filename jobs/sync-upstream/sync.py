""" sync repo script
"""
import sys

sys.path.insert(0, ".")

import click
import sh
import os
import uuid
import yaml
from pathlib import Path
from urllib.parse import urlparse
from sdk import utils
from melddict import MeldDict


@click.group()
def cli():
    pass


def _cut_stable_release(layer_list, charm_list, dry_run):
    """ This will force push each layers master onto the stable branches.

    PLEASE NOTE: This step should come after each stable branch has been tagged
    and references a current stable bundle revision.

    layer_list: YAML spec containing git repos and their upstream/downstream properties
    charm_list: YAML spec containing git repos and their upstream/downstream properties
    """
    layer_list = yaml.safe_load(Path(layer_list).read_text(encoding="utf8"))
    charm_list = yaml.safe_load(Path(charm_list).read_text(encoding="utf8"))
    new_env = os.environ.copy()
    for layer_map in layer_list + charm_list:
        for layer_name, repos in layer_map.items():
            downstream = repos["downstream"]
            if not repos.get("needs_stable", True):
                click.echo(f"Skipping :: {layer_name:^25} :: no stable branch")
                continue

            click.echo(f"Releasing :: {layer_name:^25} :: from-to: master,stable vcs-repo: {repos['downstream']}")
            if not dry_run:
                downstream = f"https://{new_env['CDKBOT_GH']}@github.com/{downstream}"
                identifier = str(uuid.uuid4())
                os.makedirs(identifier)
                for line in sh.git.clone(downstream, identifier, _iter=True):
                    click.echo(line)
                sh.git.config("user.email", "cdkbot@juju.solutions", _cwd=identifier)
                sh.git.config("user.name", "cdkbot", _cwd=identifier)
                sh.git.config("--global", "push.default", "simple")
                sh.git.branch("-f", "stable", "master", _cwd=identifier)
                for line in sh.git.push("-f", "origin", "stable", _cwd=identifier, _iter=True):
                    click.echo(line)


@cli.command()
@click.option("--layer-list", required=True, help="Path to supported layer list")
@click.option("--charm-list", required=True, help="Path to supported charm list")
@click.option("--dry-run", is_flag=True)
def cut_stable_release(layer_list, charm_list, dry_run):
    return _cut_stable_release(layer_list, dry_run)


def _tag_stable_forks(layer_list, charm_list, bundle_rev, dry_run):
    """ Tags stable forks to a certain bundle revision for a k8s version

    layer_list: YAML spec containing git repos and their upstream/downstream properties
    bundle_rev: bundle revision to tag for a particular version of k8s

    git tag (ie. ck-{bundle_rev}), this would mean we tagged current
    stable branches for 1.14 with the latest charmed kubernetes(ck) bundle rev
    of {bundle_rev}
    """
    layer_list = yaml.safe_load(Path(layer_list).read_text(encoding="utf8"))
    charm_list = yaml.safe_load(Path(charm_list).read_text(encoding="utf8"))
    new_env = os.environ.copy()
    for layer_map in layer_list + charm_list:
        for layer_name, repos in layer_map.items():
            downstream = repos["downstream"]
            tag = f"ck-{bundle_rev}"
            if not repos.get("needs_tagging", True):
                click.echo(f"Skipping {layer_name} :: does not require tagging")
                continue

            click.echo(f"Tagging {layer_name} ({tag}) :: {repos['downstream']}")
            if not dry_run:
                downstream = f"https://{new_env['CDKBOT_GH']}@github.com/{downstream}"
                identifier = str(uuid.uuid4())
                os.makedirs(identifier)
                for line in sh.git.clone(downstream, identifier, _iter=True):
                    click.echo(line)
                sh.git.config("user.email", "cdkbot@juju.solutions", _cwd=identifier)
                sh.git.config("user.name", "cdkbot", _cwd=identifier)
                sh.git.config("--global", "push.default", "simple")
                sh.git.checkout("stable", _cwd=identifier)
                sh.git.tag(tag, _cwd=identifier)
                for line in sh.git.push("origin", tag, _cwd=identifier, _iter=True):
                    click.echo(line)


@cli.command()
@click.option("--layer-list", required=True, help="Path to supported layer list")
@click.option("--charm-list", required=True, help="Path to supported charm list")
@click.option(
    "--bundle-revision", required=True, help="Bundle revision to tag stable against"
)
@click.option("--dry-run", is_flag=True)
def tag_stable(layer_list, charm_list, bundle_revision, dry_run):
    return _tag_stable_forks(layer_list, charm_list, bundle_revision, dry_run)


def _sync_upstream(layer_list, dry_run):
    """ Syncs any of the forked upstream repos

    layer_list: YAML spec containing git repos and their upstream/downstream properties
    """
    layer_list = yaml.safe_load(Path(layer_list).read_text(encoding="utf8"))
    new_env = os.environ.copy()

    for layer_map in layer_list:
        for layer_name, repos in layer_map.items():
            upstream = repos["upstream"]
            downstream = repos["downstream"]
            if urlparse(upstream).path.lstrip("/") == downstream:
                click.echo(f"Skipping {layer_name} :: {upstream} == {downstream}")
                continue
            click.echo(
                f"Syncing {layer_name} :: {repos['upstream']} -> {repos['downstream']}"
            )
            if not dry_run:
                downstream = f"https://{new_env['CDKBOT_GH']}@github.com/{downstream}"
                identifier = str(uuid.uuid4())
                os.makedirs(identifier)
                for line in sh.git.clone(downstream, identifier, _iter=True):
                    click.echo(line)
                sh.git.config("user.email", "cdkbot@juju.solutions", _cwd=identifier)
                sh.git.config("user.name", "cdkbot", _cwd=identifier)
                sh.git.config("--global", "push.default", "simple")
                sh.git.remote("add", "upstream", upstream, _cwd=identifier)
                for line in sh.git.fetch("upstream", _cwd=identifier, _iter=True):
                    click.echo(line)
                sh.git.checkout("master", _cwd=identifier)
                if "layer-index" in downstream:
                    sh.python3("update_readme.py", _cwd=identifier)
                for line in sh.git.merge(
                    "upstream/master", _cwd=identifier, _iter=True
                ):
                    click.echo(line)
                for line in sh.git.push("origin", _cwd=identifier, _iter=True):
                    click.echo(line)


@cli.command()
@click.option("--layer-list", required=True, help="Path to supported layer list")
@click.option("--dry-run", is_flag=True)
def forks(layer_list, dry_run):
    """ Syncs all upstream forks
    """
    # Try auto-merge; if conflict: update_readme.py && git add README.md && git
    # commit. If that fails, too, then it was a JSON conflict that will have to
    # be handled manually.
    return _sync_upstream(layer_list, dry_run)


if __name__ == "__main__":
    cli()
