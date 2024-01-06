# `lute3`

Learning Using Texts v3.

Lute is for learning foreign languages through reading.  `lute3` is a rewrite of the original Lute PHP application in Python and Flask.



## Requirements

Recommend version: **Python 3.10.x** (Python version bigger than 3.8 and smaller than 3.10.x is ok)

## Install

`lute3` installs various dependencies, so you should install it in a virtual environment.  For example, using `venv`:

Create a new folder (e.g. `lute3`) anywhere on your system.

```
# Set up the virtual environment
python -m venv myenv

# Activate it (Mac or *nix)
source myenv/bin/activate

# (on Windows: myenv\Scripts\activate)

# Install everything.  Note the package name is lute3!
pip install lute3

# Start lute
python -m lute.main

# Open your web browser to http://localhost:5000
# When done, hit Ctl-C

# Stop the virtual environment.
deactivate
```

Once everything is installed, for future runs you'll just need to go into `lute3` folder created above and:

```
source myenv/bin/activate
python -m lute.main
```