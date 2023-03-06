#!/usr/bin/env python

# This file is part of pre-commit-config.
#
# Developed by Michael Reuter.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

import argparse
import pathlib
import shutil

# The root of the current file to be used by the Path definitions below.
ROOT = pathlib.Path(__file__)

# Directories with data used by this script.
CONFIG_FILES_DIR = ROOT.resolve().parents[0] / "config_files"
TEMPLATES_DIR = ROOT.resolve().parents[0] / "templates"

# Config files for the pre-commit hooks.
FLAKE8_CONFIG_FILE_NAME = ".flake8"
ISORT_CONFIG_FILE_NAME = ".isort.cfg"
MYPY_CONFIG_FILE_NAME = ".mypy.ini"
PRE_COMMIT_CONFIG_FILE_NAME = ".pre-commit-config.yaml"

# Config file paths for the pre-commit hooks.
FLAKE8_CONFIG_FILE = CONFIG_FILES_DIR / FLAKE8_CONFIG_FILE_NAME
ISORT_CONFIG_FILE = CONFIG_FILES_DIR / ISORT_CONFIG_FILE_NAME
MYPY_CONFIG_FILE = CONFIG_FILES_DIR / MYPY_CONFIG_FILE_NAME

# Template files.
MYPY_PRE_COMMIT_HOOK_TEMPLATE = TEMPLATES_DIR / "mypy-pre-commit-hook-template.yaml"
PRE_COMMIT_CONFIG_TEMPLATE = TEMPLATES_DIR / "pre-commit-config-template.yaml"

DOT_GITIGNORE = ".gitignore"


def main(opts: argparse.Namespace) -> None:
    destination = pathlib.Path(opts.dest)

    with open(PRE_COMMIT_CONFIG_TEMPLATE) as f:
        pre_commit_config = f.read()
    if not args.no_mypy:
        with open(MYPY_PRE_COMMIT_HOOK_TEMPLATE) as f:
            mypy_pre_commit_config = f.read()
            if opts.mypy_extras is not None:
                extras = opts.mypy_extras.split(",")
                for extra in extras:
                    mypy_pre_commit_config += " " * 10 + f"- {extra.strip()}\n"
            pre_commit_config += mypy_pre_commit_config
    with open(pathlib.Path(destination) / PRE_COMMIT_CONFIG_FILE_NAME, "w") as f:
        f.write(pre_commit_config)

    shutil.copy(FLAKE8_CONFIG_FILE, destination)
    shutil.copy(ISORT_CONFIG_FILE, destination)
    if not opts.no_mypy:
        shutil.copy(MYPY_CONFIG_FILE, destination)

    dot_gitignore = destination / DOT_GITIGNORE
    if not dot_gitignore.exists():
        dot_gitignore.touch()

    with open(dot_gitignore) as f:
        dot_gitignore_contents = f.read()
    with open(dot_gitignore, "a") as f:
        if PRE_COMMIT_CONFIG_FILE_NAME not in dot_gitignore_contents:
            f.write(f"{PRE_COMMIT_CONFIG_FILE_NAME}\n")
        if FLAKE8_CONFIG_FILE_NAME not in dot_gitignore_contents:
            f.write(f"{FLAKE8_CONFIG_FILE_NAME}\n")
        if ISORT_CONFIG_FILE_NAME not in dot_gitignore_contents:
            f.write(f"{ISORT_CONFIG_FILE_NAME}\n")
        if MYPY_CONFIG_FILE_NAME not in dot_gitignore_contents and not opts.no_mypy:
            f.write(f"{MYPY_CONFIG_FILE_NAME}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script generates the config files for pre-commit and its hooks.",
        epilog="This script doesn't delete existing configuration files so you need to remove "
        "those manually if necessary.",
    )

    parser.add_argument(
        "--no-mypy",
        action="store_true",
        default=False,
        help="Generate a pre-commit configuration file without mypy "
        "(default: False, meaning mypy gets included).",
    )

    parser.add_argument(
        "--dest",
        default=".",
        help="The destination folder to install the pre-commit configurations files into "
        "(default: '.' meaning the current working directory). Intended to be used by "
        "scripts that update more than one project at a time.",
    )

    parser.add_argument(
        "--mypy-extras",
        help="Add extra stub package dependencies into the mypy pre-commit hook config. "
        "More than one package can be specified using a comma-delimited list.",
    )

    args = parser.parse_args()
    main(args)
