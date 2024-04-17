import argparse
import logging
import os
import sys

import tomli

from flootstrap.bootstrapper import registry
from flootstrap.bootstrappers.debootstrap import Debootstrap
from flootstrap.bootstrappers.rinse import Rinse
from flootstrap.logger import logger


class Flootstrap:
    def list(self):
        for k in registry.targets():
            print(k)

    def build_all(self, config, config_path):
        for e in config:
            self.build_entry(config, config_path, e)

    def build_entry(self, config, config_path, entry):
        entry_config = config[entry]
        target = entry_config["target"]
        try:
            cls = registry.find(target)[0]
        except IndexError:
            logger.critical(f"Missing target '{target}'")
            return
        # TODO Transform paths if relative
        cls.bootstrap(target, entry_config["arch"], entry_config["dir"])

    def build(self, config, config_path, entry=None):
        if not entry:
            self.build_all(config, config_path)
        else:
            self.build_entry(config, config_path, entry)


def run():
    levels = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    # Options
    parser = argparse.ArgumentParser(prog="flootstrap")
    parser.add_argument(
        "-l",
        "--log",
        default="warning",
        choices=[x for x in levels],
        help=("Provide logging level. "),
    )
    subparser = parser.add_subparsers(title="commands", dest="command")
    # Build subcommand
    build_args = subparser.add_parser("build", help="Build for a specific target")
    build_args.add_argument("config", help="Configuration file")
    build_args.add_argument("-e", "--entry", help="Entry in the config file to build")
    # List subcommand
    list_args = subparser.add_parser("list", help="List available targets")

    # Parse the options, if any
    args = parser.parse_args(sys.argv[1:])
    level = levels[args.log.lower()]
    logger.setLevel(level)

    # Register the available bootstrappers
    registry.register(Debootstrap)
    registry.register(Rinse)

    f = Flootstrap()
    if args.command == "list":
        f.list()
    elif args.command == "build":
        # Parse the config file
        with open(args.config, "rb") as fconfig:
            config_path = os.path.dirname(os.path.realpath(fconfig.name))
            config = tomli.load(fconfig)
            # invoke the corresponding bootstrapper
            f.build(config, config_path)
