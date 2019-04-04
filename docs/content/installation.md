# Installation

This page documents how to get `pxl` up and running. We will install:

 - Python 3.7
 - `pipenv`

## Ubuntu

Python 3.7 isn't packaged for Ubuntu. We need to configure Apt to fetch
packages from the [`deadsnakes`][deadsnakes] ppa before we can install it.
Also install `git`, which we'll need later.

```
$ sudo apt install software-properties-common git
$ sudo add-apt-repository ppa:deadsnakes
$ sudo apt update
```

Now that the PPA is configured, we can install Python 3.7 and `pip`:

```
$ sudo apt install python3.7 python3.7-dev python3-pip
```

`pxl` needs [`pipenv`][pipenv]. We will use `pip` to install it:

```
$ pip3 install --user --upgrade pipenv
```

`pipenv` needs to be in your `$PATH`. The `--user` flag of `pip` means it got
installed in `$HOME/.local/bin`. Open your shell config (probably `~/.bashrc`)
and add the following line to the bottom:

```
export PATH="$HOME/.local/bin:$PATH"
```

Open a new terminal, and type `pipenv help`. That should print some output
other than `pipenv: Command not found`.

We're almost there! Up next is actually getting `pxl` and running it. Get the
code, install python dependencies, and run everything:

```
# Get the code and change directories
$ git clone https://github.com/svsticky/pxl.git
$ cd pxl

# Install dependencies
$ pipenv sync

# Run the app! It should print a help page.
$ pipenv run pxl
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Photo management script for S3 albums.

Options:
  --help  Show this message and exit.

Commands:
  build    Build a static site based on current state.
  clean    Clean pxl files from system
  deploy   Deploy the static output.
  init     Initialize pxl configuration
  preview  Run a local webserver on build output
  upload   Upload a directory to the photo hosting.
```

If you saw this: Congrats! You're golden!

 [deadsnakes]: https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
 [pipenv]: https://github.com/pypa/pipenv
