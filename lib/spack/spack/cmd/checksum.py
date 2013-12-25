import os
import re
import argparse
import hashlib
from pprint import pprint
from subprocess import CalledProcessError

import spack.tty as tty
import spack.packages as packages
import spack.util.crypto
from spack.stage import Stage, FailedDownloadError
from spack.colify import colify
from spack.version import *

description ="Checksum available versions of a package to update a package file."

def setup_parser(subparser):
    subparser.add_argument(
        'package', metavar='PACKAGE', help='Package to list versions for')
    subparser.add_argument(
        'versions', nargs=argparse.REMAINDER, help='Versions to generate checksums for')


def get_checksums(versions, urls, **kwargs):
    # Allow commands like create() to do some analysis on the first
    # archive after it is downloaded.
    first_stage_function = kwargs.get('first_stage_function', None)

    tty.msg("Downloading...")
    hashes = []
    for i, (url, version) in enumerate(zip(urls, versions)):
        stage = Stage(url)
        try:
            stage.fetch()
            if i == 0 and first_stage_function:
                first_stage_function(stage)

            hashes.append(
                spack.util.crypto.checksum(hashlib.md5, stage.archive_file))
        except FailedDownloadError, e:
            tty.msg("Failed to fetch %s" % url)
            continue

        finally:
            stage.destroy()

    return zip(versions, hashes)


def checksum(parser, args):
    # get the package we're going to generate checksums for
    pkg = packages.get(args.package)

    # If the user asked for specific versions, use those.
    versions = [ver(v) for v in args.versions]

    if not all(type(v) == Version for v in versions):
        tty.die("Cannot generate checksums for version lists or " +
                "version ranges.  Use unambiguous versions.")

    if not versions:
        versions = pkg.fetch_available_versions()
        if not versions:
            tty.die("Could not fetch any available versions for %s." % pkg.name)

    versions = list(reversed(versions))
    urls = [pkg.url_for_version(v) for v in versions]


    tty.msg("Found %s versions of %s." % (len(urls), pkg.name),
            *["%-10s%s" % (v,u) for v, u in zip(versions, urls)])
    print
    archives_to_fetch = tty.get_number(
        "How many would you like to checksum?", default=5, abort='q')

    if not archives_to_fetch:
        tty.msg("Aborted.")
        return

    version_hashes = get_checksums(
        versions[:archives_to_fetch], urls[:archives_to_fetch])

    if not version_hashes:
        tty.die("Could not fetch any available versions for %s." % pkg.name)

    dict_string = ["    '%s' : '%s'," % (v, h) for v, h in version_hashes]
    dict_string = ['{'] + dict_string + ["}"]

    tty.msg("Checksummed new versions of %s:" % pkg.name, *dict_string)