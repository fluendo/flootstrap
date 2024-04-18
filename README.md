## Overview

Flootstrap is a python wrapper around Linux distributions bootstrappers.
Chroot's environments are useful for building locally in a native guest environment
and don't pollute your system with dependencies.

There are other alternatives for isolating a system for building and testing, but
unlike container-based alternatives like `Docker`, this only abstracts the file system,
not the system as a whole.

## Examples
```toml
[debian-bookworm]
target = 'debian-bookworm'
arch = 'amd64'
dir = 'debian-bookworm-amd64'
post_script = 'post-script.sh'

[fedora-28]
target = 'fedora-28'
arch = 'amd64'
dir = 'fedora-28-amd64'
post_script = 'post-script.sh'
```

## Running
### Listing available distributions and versions
```shell
$> flootstrap -l debug list
```

### Building the entries on the file
```shell
$> flootstrap -l debug build examples/rootfs.toml
```

### Running a command inside the rootfs
```shell
$> flootstrap -l debug run examples/rootfs.toml debian-bookworm /bin/bash
```
## TODO
* [ ] Add support for ENV variables in the toml definition
* [ ] Call the post-script after the rootfs is created
* [ ] Add support for extra command line options when triggering the bootstrapper
* [ ] Fix rinse error `Use of uninitialized value $CONFIG{"width"} in subtraction (-) at /usr/sbin/rinse line 1247`
