#!/usr/bin/env python
"""
Setup the development environment.

Runs the following commands:
{}
"""
import argparse
import os

from show_env import execute_command_list

commands_to_run = [
    # pip >=19.0.0,<19.0.3 (so far) cause problems with some package installs,
    # so pin pip below v19 until that problem is resolved.
    ["poetry", "run", "pip", "install", "--upgrade", "pip<19", "setuptools"],
    ["poetry", "install"],
    ["poetry", "run", "pre-commit", "install"],
]

__doc__ = __doc__.format("\n".join(map(" ".join, commands_to_run)))


def env_setup(verbose):
    """Prepare environment for running."""
    print("In: {}".format(os.getcwd()))
    print("Setting up Virtual Environment: {}".format(os.environ.get("VIRTUAL_ENV")))

    execute_command_list(commands_to_run, verbose=verbose)


def main():
    """Execute env_setup using command line args."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show each command before it is executed",
    )
    args = parser.parse_args()
    env_setup(args.verbose)


if __name__ == "__main__":
    main()
