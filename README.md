## Overview

Flootstrap is a python wrapper around Linux distributions bootstrappers.
Chroot's environments are useful for building locally in a native guest environment
and don't pollute your system with dependencies.

There are other alternatives for isolating a system for building and testing, but
unlike container-based alternatives like `Docker`, this only abstracts the file system,
not the system as a whole.

## Examples
```toml
[rootfs]
name = 'Debian Wheezy'
flavor = 'wheezy'
dir = 'debian-wheezy'
post_script = 'post-script.sh'
```

## Running
