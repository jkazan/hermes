# Hermes CLI
### Running in Python3

### Dependencies for mac and linux
* requests

### Dependencies for windows
* requests
* pyreadline

### Recommendation
Run Hermes in a virtual environment with `virtualenv`
https://virtualenv.pypa.io/en/latest/

### On ubuntu
Install python3 and pip3
```sh
$ apt-get install python3 python3-pip
```
Install dependencies
```sh
$ pip3 install requests
```
Run
```sh
$ python3 <path to hermes>/hermes.py
```

### On mac
Install python3 and pip3
```sh
$ brew install python3
$ brew postinstall python3
```
Install dependencies
```sh
$ pip3 install requests
```
Run
```sh
$ python3 <path to hermes>/hermes.py
```

### On windows
* Download latest python version 64 bit from
https://www.python.org/downloads/windows/

* During installation process: Check the checkbox to add python to path

* Press windows+r to open 'Run', enter "cmd" and press "OK".

Upgrade pip
```sh
python -m pip install --upgrade pip
```
Install dependencies
```sh
pip install pyreadline requests
```
Run
```sh
python <path to hermes>/hermes.py
```

### Caveat

This cli was developed to improve my workflow. Not all features for Jira has been implemented. The tool is provided as is.
