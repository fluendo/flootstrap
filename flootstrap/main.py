import argparse
import logging
import os
import pwd
import subprocess
import sys
import time

import tomli

from flootstrap.bootstrapper import registry
from flootstrap.bootstrappers.debootstrap import Debootstrap
from flootstrap.bootstrappers.rinse import Rinse
from flootstrap.logger import logger
from flootstrap.utils import execute


class Flootstrap:
    def list(self):
        for k in registry.targets():
            print(k)

    def generate_sudoers(self, user, d):
        sudoers = os.path.join(d, "etc", "sudoers")
        execute(["sh", "-c", f"echo {user} ALL=NOPASSWD: ALL > {sudoers}"], sudo=True)
        execute(["chmod", "440", f"{sudoers}"], sudo=True)

    def run(self, root, config, config_path, entry, cmd):
        entry_config = config[entry]
        d = entry_config["dir"]
        mps = ["dev", "sys", "proc", "tmp"]
        files = [
            "etc/hosts.conf",
            "etc/hosts",
            "etc/nsswitch.conf",
            "etc/passwd",
            "etc/group",
            "etc/shadow",
        ]
        # Mount the common folders
        for mp in mps:
            src = os.path.join("/", mp)
            dst = os.path.join(d, mp)
            self.bind_mount(src, dst)
        # Copy host files
        for f in files:
            src = os.path.join("/", f)
            dst = os.path.join(d, f)
            execute(["cp", src, dst], sudo=True)
        # Mount the home folder
        uname = pwd.getpwuid(os.getuid())[0]
        grpid = pwd.getpwuid(os.getuid())[3]
        self.mount_home(uname, grpid, d)
        # Mount the special pts
        self.mount_pts(d)
        # Setup sudoers
        self.generate_sudoers(uname, d)
        # Execute the command
        chroot = ["sudo"]
        if not root:
            chroot = chroot + [
                f"USER={uname}",
                f"HOME=/home/{uname}",
                "chroot",
                f"--userspec={uname}:{grpid}",
            ]
        else:
            chroot = chroot + ["chroot"]
        chroot = chroot + [d, cmd]
        try:
            logger.debug(f"Executing {chroot}")
            subprocess.call(chroot)
        except:
            pass
        # Unmount
        # Give some time for every bind to be ready to umount
        logger.debug("Waiting 2s before umounting ...")
        time.sleep(2)
        self.umount_pts(d)
        self.umount_home(uname, d)
        for mp in reversed(mps):
            dst = os.path.join(d, mp)
            self.umount(dst)

    def mount_pts(self, d):
        pts = os.path.join(d, "dev", "pts")
        execute(["mount", "-t", "devpts", "none", pts], sudo=True)

    def umount_pts(self, d):
        pts = os.path.join(d, "dev", "pts")
        self.umount(pts)

    def mount_home(self, user, group, d):
        src_home = os.path.join("/", "home", user)
        dst_home = os.path.join(d, "home", user)
        execute(["mkdir", "-p", dst_home], sudo=True)
        execute(["chown", f"{user}:{group}", dst_home], sudo=True)
        self.bind_mount(src_home, dst_home)

    def umount_home(self, user, d):
        dst_home = os.path.join(d, "home", user)
        self.umount(dst_home)

    def bind_mount(self, src, dst):
        logger.info(f"Bind-mounting '{src}' into '{dst}'")
        execute(["mount", "--bind", src, dst], sudo=True)

    def umount(self, dst):
        logger.info(f"Unmounting '{dst}'")
        execute(["umount", dst], sudo=True)

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
        help=("Provide logging level"),
    )
    subparser = parser.add_subparsers(title="commands", dest="command")
    # Build subcommand
    build_args = subparser.add_parser("build", help="Build a specific entry")
    build_args.add_argument("config", help="Configuration file")
    build_args.add_argument("-e", "--entry", help="Entry in the config file to build")
    # List subcommand
    list_args = subparser.add_parser("list", help="List available targets")
    # Shell subcommand
    run_args = subparser.add_parser("run", help="Execute a command inside an entry")
    run_args.add_argument("config", help="Configuration file")
    run_args.add_argument("entry", help="Entry to run the command into")
    run_args.add_argument("cmd", help="Command to execute")
    run_args.add_argument(
        "-r", "--root", action="store_true", help="Use root as the user"
    )

    # Parse the options, if any
    args = parser.parse_args(sys.argv[1:])
    level = levels[args.log.lower()]
    logger.setLevel(level)

    # Register the available bootstrappers
    registry.register(Debootstrap)
    registry.register(Rinse)

    # TODO check for the existance of sudo

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
    elif args.command == "run":
        # Parse the config file
        with open(args.config, "rb") as fconfig:
            config_path = os.path.dirname(os.path.realpath(fconfig.name))
            config = tomli.load(fconfig)
            f.run(args.root, config, config_path, args.entry, args.cmd)
