from flootstrap.bootstrapper import Bootstrapper
from flootstrap.logger import logger


class Rinse(Bootstrapper):
    cmd = "rinse"

    @classmethod
    def list(cls):
        skipped = False
        targets = []
        for line in cls.execute([cls.cmd, "--list-distributions"]):
            if not skipped:
                skipped = True
                continue
            # Rinse outputs targets in the form name-version
            target = line.rsplit("-", 1)
            targets.append((target[0], target[1]))
        return targets

    @classmethod
    def bootstrap(cls, target, arch, path):
        for line in cls.execute(
            [cls.cmd, "--distribution", target, "--arch", arch, "--directory", path],
            sudo=True,
        ):
            logger.info(line)
