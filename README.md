# Hermes CLI
### Running in Python3

### Dependencies
* requests

### Install on mac
Install python3 and pip3
```sh
$ brew install python3
$ brew postinstall python3
```
Install package 'requests'
```sh
$ sudo pip3 install requests
```

### Install on ubuntu
Install python3 and pip3
```sh
$ sudo apt-get install python3 python3-pip
```
Install package 'requests'
```sh
$ sudo pip3 install requests
```

### Run
```sh
$ python3 <path to hermes>/hermes.py
```

### Caveat

This cli was developed to improve my workflow. I am lacking knowledge
regarding Jira's json structure, resulting in imperfections when
printing list of tickets, have been desiged based on my personal
tickets. Furthermore, only a small selection of features habe been
implemented, based on my own need. Please feel free to contribute!