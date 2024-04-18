import subprocess

from flootstrap.logger import logger


def execute_iter(cmd, sudo=False, shell=False):
    if sudo:
        cmd = ["sudo"] + cmd

    logger.debug(f"Executing iteratively'{' '.join(cmd)}'")
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


def execute(cmd, sudo=False, shell=False):
    if sudo:
        cmd = ["sudo"] + cmd

    logger.debug(f"Executing '{' '.join(cmd)}'")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        shell=shell,
        universal_newlines=True,
    )
    out, err = process.communicate()
    if out:
        for line in out.splitlines():
            logger.debug(line)
    if err:
        for line in err.splitlines():
            logger.error(line)
    return process.returncode
