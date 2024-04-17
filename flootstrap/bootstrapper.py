import shutil
import subprocess

from flootstrap.logger import logger


class Bootstrapper:
    cmd = None

    @classmethod
    def list(cls):
        """
        List available targets
        Returns a list of tuples in the form (distribution, target)
        """
        raise NotImplementedError

    @classmethod
    def bootstrap(cls, target, arch, path):
        raise NotImplementedError

    @classmethod
    def exists(cls):
        """
        Check if the boostrapper exists
        """
        logger.debug(f"Checking for the existance of the executable '{cls.cmd}'")
        return False if not shutil.which(cls.cmd) else True

    @classmethod
    def execute(cls, cmd, sudo=False, shell=False):
        if sudo:
            cmd = ["sudo"] + cmd

        logger.debug(f"Executing '{' '.join(cmd)}'")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            shell=shell,
            universal_newlines=True,
        )
        for line in iter(process.stdout.readline, ""):
            yield line.strip()


class BootstrapRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, cls):
        if cls.exists():
            logger.debug(f"Executable '{cls.cmd}' exists, registering the targets")
            # list all and register them
            for e in cls.list():
                key = f"{e[0]}-{e[1]}"
                if not key in self._registry:
                    self._registry[key] = []
                self._registry[key].append(cls)

    def targets(self):
        return self._registry.keys()

    def find(self, target):
        return self._registry.get(target, [])


registry = BootstrapRegistry()
