#! /usr/bin/env python
"""
A simple module/program to show the behave banner and environment.

When invoked as a program, it shows the behave banner and environment.

When used as a module, it also defines a nice helper function:
execute_command_list - run commands in a list;
on failure, exit w/ helpful message and error status.
"""
import sys
from os import environ
from os.path import exists
from shutil import copyfileobj
from subprocess import CalledProcessError
from subprocess import check_call


# Define this here because it is needed by the other scripts.
def execute_command_list(commands_to_run, verbose=True):
    """
    Execute each command in the list.

    If any command fails, print a helpful message and exit with that status.
    """
    for command in commands_to_run:
        readable_command = " ".join(command)
        try:
            if verbose:
                print(readable_command)
            check_call(command)
        except CalledProcessError as e:
            print(
                '"{}" - returned status code "{}"'.format(
                    readable_command, e.returncode
                )
            )
            exit(e.returncode)
        except FileNotFoundError as f:
            print(
                '"{}" - No such file/program: "{}"'.format(readable_command, f.filename)
            )
            exit(2)


BEHAVE_CONFIG_FILES = [".behaverc", "behave.ini"]

ENV_VAR_PREFIX = "BEHAVE_"

# Split BANNER in half because it has funky ascii that
# will interfere with Python .format() processing :-)
BANNER = r"""
     [Given]              [When]               [Then]
        _                  ( ( (           \    ....    /
    ___|_|___              ) ) )              /      \
 __|         |__        ..........      --   {        }   --
 \ |         |--|       |        |__          \      /
  \|         | )|       |        |_ \      /   )    (   \
   |         |_)|       |        |_| |         |    |
   |         |--|       |        |__/          (----)
    \_______/           |________|             (----)

               === Behave Test Runner ==="""


BANNER2 = """
========================================================
              BEHAVE Environment Configuration
--------------------------------------------------------
{}
{}

Environment variables:"""


END_BANNER = """\
========================================================"""


def show_env():
    """Display environment data."""
    print(BANNER)
    virtual_env = environ.get("VIRTUAL_ENV")
    docker_env = environ.get("PRECONFIGURED_DOCKER")
    if virtual_env is not None:
        print(
            BANNER2.format(
                "Running in virtual environment:", environ.get("VIRTUAL_ENV")
            )
        )
    elif docker_env is not None:
        print(BANNER2.format("Preconfigured Docker environement", ""))
    else:
        print(BANNER2.format("No virtual environment!", ""))

    for k, v in sorted(environ.items()):
        if not k.startswith(ENV_VAR_PREFIX):
            continue
        print("{}={}".format(k, v))

    for config_file in filter(exists, BEHAVE_CONFIG_FILES):
        print()
        print("Configuration from {}:".format(config_file))
        with open(config_file) as f:
            copyfileobj(f, sys.stdout)

    print(END_BANNER)


if __name__ == "__main__":
    show_env()
