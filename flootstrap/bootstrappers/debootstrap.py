import os
import re

from flootstrap.bootstrapper import Bootstrapper
from flootstrap.logger import logger


class Debootstrap(Bootstrapper):
    cmd = "debootstrap"

    @classmethod
    def list(cls):
        # We need to iterate over /usr/share/debootstrap/script
        # Check every file contents and check of either debian or ubuntu
        targets = []
        # Ubuntu
        for line in cls.execute(
            ["grep", "-Rl", "ubuntu.com", "/usr/share/debootstrap/scripts/"]
        ):
            version = os.path.basename(line)
            # If a file has an extension, is a variant, skip it
            if os.path.splitext(version)[1]:
                continue
            targets.append(("ubuntu", version))
        # Debian
        for line in cls.execute(
            ["grep", "-Rl", "debian-common", "/usr/share/debootstrap/scripts/"]
        ):
            version = os.path.basename(line)
            # Kali
            if "kali" in version:
                kali = version.split("-", 1)
                targets.append(("kali", kali[1] if len(kali) > 1 else ""))
            else:
                targets.append(("debian", version))
        return targets

    @classmethod
    def bootstrap(cls, target, arch, path):
        # debootstrap --arch amd64 stretch ./stretch-chroot
        texploded = target.split("-", 1)
        if not texploded[1]:
            version = texploded[0]
        else:
            version = texploded[1]

        for line in cls.execute([cls.cmd, "--arch", arch, version, path], sudo=True):
            # The log info is in the form
            # I: Keyring file not available at /usr/share/keyrings/debian-archive-keyring.gpg; switching to https mirror https://deb.debian.org/debian
            m = re.match(r"(?P<level>[IE]): (?P<message>.*)", line)
            if m.group("level") == "I":
                logger.info(m.group("message"))
            elif m.group("level") == "E":
                logger.error(m.group("message"))
