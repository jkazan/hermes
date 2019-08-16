# Hermes CLI

### Prerequisites
Python3



### For Linux/Mac

##### Install
```sh
git clone https://github.com/jkazan/hermes.git
cd hermes
python3 setup.py install
```

##### Run
```sh
python3 hermes/hermes.py
```



### For Windows
Go to [`python.org`](https://docs.python.org/downloads/windows) and download latest python3 stable version. When running the installation, check "Add Python 3.X to PATH".

##### Install
Download hermes

Open Command Prompt (search for "cmd" in start menu) and type:
```sh
cd <path to hermes, e.g. C:\Users\johnsmith\hermes-master>
python setup.py install
pip install pyreadline
```

##### Run
```sh
python hermes/hermes.py
```


### Usage
Examples:

Comment on ticket Jira ICSHWI-2919
```sh
comment ICSHWI-2919 "This is my comment"
```

Get all comments on Jira ticket ICSHWI-2919
```sh
comments ICSHWI-2919
```

Log work to Jira ticket ICSHWI-2919
```sh
log ICSHWI-2919 "3h 30m" "This is a worklog comment"
```

List all ESS Jira projects
```sh
projects
```

Change the state of ICSHWI-2919 to "In Progress"
```sh
state ICSHWI-2919 "In Progress"
```

Create a subtask with ICSHWI-1391 as parent ticket and 6 hour estimated effort
```sh
subtask ICSHWI-1391 "This is the task title" "6h"
```

Get a list of all your Jira tickets
```sh
tickets
```

Get a list of e.g. John Smith's Jira tickets
```sh
tickets johnsmith
```

Generate weekly report email with my achievements (
```sh
report
```

### Caveat

This CLI was developed to improve my workflow. Not all features for Jira has been implemented. The tool is provided as is.