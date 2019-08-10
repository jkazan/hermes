from __future__ import print_function
from datetime import datetime, timedelta
import os
import sys
import subprocess
import readline
import json
from terminal import Write as W
import requests
import getpass
import inspect
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from graph import JiraSearch
import textwrap

import threading
import time

class HJira(object):

    def __init__(self):
        self.user = None
        self.mailaddress = None
        self.lm_mailaddress = None
        self.auth = (self.user, None)
        self.headers = {'Content-Type':'application/json'}
        self.stoprog = False
        self.loggedin = False
        self.user_file = 'jira_cli.user'
        self.stop = False

        self.store_user()

    def store_user(self):
        path = os.path.dirname(os.path.abspath(__file__))

        if os.path.isfile(path+'/'+self.user_file):
            with open(path+'/'+self.user_file, 'r') as fr:
                json_data = json.load(fr)
                self.user = json_data['user']
                self.mailaddress = json_data['email']
                self.lm_mailaddress = json_data['lm_email']
        else:
            first = input("First name: ").lower()
            last = input("Last name: ").lower()
            self.user = "{}{}" .format(first, last)
            self.mailaddress = "{}.{}@esss.se" .format(first, last)
            lm_first = input("Line manager's first name: ").lower()
            lm_last = input("Line manager's last name: ").lower()
            self.lm_mailaddress = "{}.{}@esss.se" .format(lm_first, lm_last)

            with open(path+'/'+self.user_file, 'w') as fw:
                info = {
                    "user":self.user,
                    "email":self.mailaddress,
                    "lm_email":self.lm_mailaddress,
                    }
                fw.write(json.dumps(info, indent=4, separators=(",", ":")))

    def email(self, recipient, subject, body, html=False):
        self.login()
        if not self.loggedin:
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.mailaddress
        msg['To'] = recipient

        if html:
            body = MIMEText(body, 'html')

        msg.attach(body)

        try:
            server = smtplib.SMTP('mail.esss.lu.se', 587)
            server.starttls()
            server.login(self.user, self.auth[1])
            server.sendmail(self.mailaddress, recipient, msg.as_string())
            server.close()
            W().write('\nCheck your email ;)\n', 'ok')
        except:
            W().write('Failed to send  mail\n', 'warning')

    def login(self, user=None, password=None):
        """" Login to Jira account. """

        if self.loggedin:
            return

        try:
            login_try = 0
            while login_try < 2:
                password = getpass.getpass("Password: ")
                self.auth = (self.user, password)
                url = 'https://jira.esss.lu.se/rest/api/2/search?jql=assignee=' + self.user
                response = requests.get(url, auth=self.auth, headers=self.headers)
                self.loggedin = self.response_ok(response)
                if self.loggedin:
                    return
                else:
                    W().write('try again\n', 'warning')
                    login_try += 1
        except Exception as e:
            W().write(e, 'warning')
            return False

        return


    def username(self, action):
        """Settings for logged in user.

        Username can be stored in local file, or removed from
        it. Remembering the username will enable logging into Jira using
        password only.

        param action: 'remember' or 'forget' username
        """
        path = os.path.dirname(os.path.abspath(__file__))

        if action == 'remember':
            with open(path+'/'+self.user_file, 'w') as f:
                f.write('{"user":"'+self.user+'"}')
                W().write('{} will be remembered\n' .format(self.user), 'ok')
        elif action == 'forget':
            if os.path.isfile(path+'/'+self.user_file):
                os.remove(path+'/'+self.user_file)
                W().write('{} has been forgotten\n' .format(self.user), 'ok')
            else:
                W().write('{} was not known\n' .format(self.user), 'warning')
        else:
            W().write('Invalid action \'{}\'\n' .format(action), 'warning')

    def state(self, ticket, state):
        self.login()
        if not self.loggedin:
            return

        state_id = ""
        if state.lower() == "backlog":
            state_id = "11"
        elif state.lower() == "in progress":
            state_id = "31"
        elif state.lower() == "implemented":
            state_id = "51"
        else:
            W().write("Invalid state '{}'" .format(state), 'warning')
            return


        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'
        url += '{}/transitions?expand=transitions.fields' .format(ticket)

        # for state_id in range(32,100):
        payload = {"transition": {"id": state_id}}
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=json.dumps(payload))
        # print("{}: {}" .format(state_id, response.status_code))
        self.response_ok(response)


        # payload = {
        #         "update": {
        #             "comment": [
        #                 {"add": {"body": comment}}
        #                 ]
        #             },
        #         "transition": {"id": state}
        #         }

    def task(self, summary, description=""):
        self.login()
        if not self.loggedin:
            return

        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'
        payload = {
            "fields": {
                "project": {"key": "ICSHWI"},
                "summary": summary,
                "description": description,
                "assignee":{"name":self.user},
                "issuetype": {
                    "name": "Task"
                    }
                }
            }

        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=json.dumps(payload))
        self.response_ok(response)

    def subtask(self, parent, summary, effort):
        self.login()
        if not self.loggedin:
            return

        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'
        project = parent.split("-")[0]
        payload = {
            "fields":{
                "project":{"key":project},
                "parent":{"key": parent},
                "summary":summary,
                "description":"Subtask",
                "assignee":{"name":self.user},
                "issuetype":{"name": "Sub-task"},
                "timetracking":{
                    "originalEstimate": effort,
                    "remainingEstimate": effort,
                    }
                # "priority":{"name":"Major"}
                },
            "update":{
                "issuelinks":[{
                     "add":{
                         "type":{
                             "name":"Relates",
                             "inward":"contains",
                             "outward":"is part of"
                            },
                         "outwardIssue":{"key":parent}
                        }
                    }
                ]
            }
        }
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=json.dumps(payload))
        self.response_ok(response)

    def comment(self, ticket, comment):
        """Comment on a Jira ticket.

        param ticket: Jira ticket key.
        param comment: Comment to post to ticket.
        """
        self.login()
        if not self.loggedin:
            return

        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'+ticket+'/comment'
        payload = '{"body":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload.encode('utf8'))
        self.response_ok(response, ticket)

    def comments(self, ticket):
        """Get comments on a Jira ticket.

        param ticket: Jira ticket key.
        """
        self.login()
        if not self.loggedin:
            return

        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'+ticket+'/comment'
        response = requests.get(url, auth=self.auth, headers=self.headers)

        if not self.response_ok(response, ticket):
            return

        data = response.json()
        raw_com = data['comments']

        names = []
        comments = []
        for i in range(len(raw_com)):
            names.append(raw_com[i]['author']['displayName'])
            comment = raw_com[i]['body']
            comments.append(comment.replace('\n', '').replace('\r', ''))

        rows, cols = os.popen('stty size', 'r').read().split()
        max_len = len(max(names, key=len)) + 1
        for i in range(len(names)):
            if i % 2 == 0:
                color = 'task'
            else:
                color = 'epic'
            spacing = " "*(max_len - len(names[i]))
            W().write('{}:{}' .format(names[i], spacing), color)

            line_len = max_len + 1
            col_nbr = 0
            for k in range(len(comments[i])):
                col_nbr += 1
                if line_len + col_nbr == int(cols):
                    col_nbr = 0
                    W().write('\n{}' .format(" "*(max_len+1)))
                    if comments[i][k] == ' ':
                        continue

                W().write('{}' .format(comments[i][k]), color)
            print('')

    def log(self, ticket, time, comment):
        """Log work.

        param ticket: Jira ticket key.
        param time: Time spent to post to ticket's work log..
        param comment: Comment to post to ticket's work log.
        """
        self.login()
        if not self.loggedin:
            return

        url = 'https://jira.esss.lu.se/rest/api/2/issue/'+ticket+'/worklog'
        payload = '{"timeSpent":"'+time+'","comment":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload.encode('utf8'))
        self.response_ok(response, ticket)

        return response

    def response_ok(self, response, ticket=None):
        """Parse Jira response message

        :param response: Jira response message
        :param ticket: Jira ticket

        :returns: True if request was successful, False otherwise
        """
        # data = response.json()
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # caller = calframe[1][3]

        if response.status_code == 200:
            return True # Successful 'get'
        elif response.status_code == 201:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            caller = calframe[1][3]
            data = response.json()
            if caller == 'task' or caller == 'subtask':
                W().write('Created {}\n' .format(data['key']), 'ok')
            else:
                W().write('Successfully posted\n', 'ok')

            return True
        elif response.status_code == 204:
            W().write('Success\n', 'ok')
            return True
        elif response.status_code == 400 or response.status_code == 404:
            data = response.json()
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            caller = calframe[1][3]
            if data['errorMessages']:
                errorMessages = data['errorMessages'][0]
                W().write('{}\n' .format(errorMessages), 'warning')
            if caller == 'assign':
                errors = data['errors']['assignee']
                W().write('{}\n' .format(errors), 'warning')
            elif caller == 'log':
                pass
                # errors = data['errors']['timeLogged']
                # W().write('{}\n' .format(errors), 'warning')
            elif caller == 'subtask':
                errors = data["errors"]
                W().write('{}\n' .format(errors), 'warning')
            # else:
            #     print(data)
        elif response.status_code == 403:
            W().write('Forbidden\nThis may be caused by too many attempts '
                          +'to enter your password. If this is the \n'
                          +'case, visit your jira domain in a browser, logout and login again. This will \n'
                          +'reset the count and Hermes will work once again.\n'
                          , 'warning')
        else:
            W().write(str(response.status_code)+"\n", 'warning')

        return False

    def tickets(self, key=None, target='assignee'):
        """Lists all tickets for assigned to a user or project.

        :param key: Name of Jira user or project
        :param target: 'assignee' or 'project', default is 'assignee'
        """
        self.login()
        if not self.loggedin:
            return

        if key is None and target == 'assignee':
            key = self.user

        url = 'https://jira.esss.lu.se/rest/api/2/search?jql='+target+'=' + key + '&maxResults=999'
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response_ok = self.response_ok(response)
        if response_ok is False:
            return

        data = response.json()
        issues = data['issues']

        if self.user == "marinovojneski": #TODO: this was a quick fix for Marino
            for i in issues:
                statlim = 6
                st = i['fields']['status']['name']
                status = st[0:statlim]+'.' if len(st)>statlim else st

                try:
                    prog = str(i['fields']['aggregateprogress']['percent']) + '%'
                except:
                    prog = ""

                s = i['fields']['summary']
                sumlim = 31
                summary = s[0:sumlim]+'...' if len(s)>sumlim+3 else s

                W().write('{:<16s}{:<14s}{:<9s}{:<7s}{}\n'
                            .format(i['key'],
                                        i['fields']['issuetype']['name'],
                                        status,
                                        prog,
                                        summary))
            return

        if not issues:
            W().write('No tickets found for \'{}\' \n' .format(key),'warning')
            return

        tickets = {}
        # Find all parents
        for i in range(0, len(issues)):
            key = issues[i]['key']
            fields = issues[i]['fields']
            tickets[key] = self.makeTicket(key, fields)

        for i in range(0, len(issues)):
            key = issues[i]['key']
            if tickets[key]['parent'] is not None:
                if tickets[key]['parent']['key'] not in tickets:
                    new_key = tickets[key]['parent']['key']
                    new_fields = tickets[key]['parent']['fields']
                    tickets[new_key] = self.makeTicket(new_key, new_fields, True)

        # Print headers
        W().write('{:<16s}{:<14s}{:<9s}{:<7s}{}\n' .format('Ticket',
                                                  'Type',
                                                  'Status',
                                                  'Prog.',
                                                  'Summary'), 'header')

        # TODO: slow sorting, fix!
        for key, data in tickets.items():
            if data['parent'] is None:
                W().write('{:<16s}{:<14s}{:<9s}{:<7s}{}\n' .format(key,
                                                        data['issuetype'],
                                                        data['status'],
                                                        data['progress'],
                                                        data['summary']), 'epic')
                for k, d in tickets.items():
                    try:
                        if d['parent']['key'] == key:
                            W().write('  {:<14s}{:<14s}{:<9s}{:<7s}{}\n' .format(k,
                                                        d['issuetype'],
                                                        d['status'],
                                                        d['progress'],
                                                        d['summary']), 'task')
                    except:
                        pass

        return tickets

    def makeTicket(self, key, fields, nonOwned=False):
        ticket = {
                'summary' : '',
                'issuetype' : '',
                'progress' : '',
                'parent' : '',
                'status' : '',
                }

        s = fields['summary']
        sumlim = 31
        ticket['summary'] = s[0:sumlim]+'...' if len(s)>sumlim+3 else s
        ticket['issuetype'] = fields['issuetype']['name']
        st = fields['status']['name']
        statlim = 6
        ticket['status'] = st[0:statlim]+'.' if len(st)>statlim else st


        if nonOwned:
            ticket['parent'] = None
            return ticket

        try:
            ticket['progress'] = str(fields['aggregateprogress']['percent']) + '%'
        except Exception:
            ticket['progress'] = ''

        try:
            ticket['parent'] = fields['parent']
        except:
            ticket['parent'] = None

        if ticket['parent'] == None:
            pkey = fields['customfield_10008']
            if pkey is None:
                ticket['parent'] = None
            else:
                ticket['parent'] = {}
                ticket['parent']['key'] = pkey
                ticket['parent']['fields'] = {}
                ticket['parent']['fields']['issuetype'] = {}
                ticket['parent']['fields']['issuetype']['name'] = 'Epic'
                ticket['parent']['fields']['summary'] = 'epic'
                ticket['parent']['fields']['aggregateprogress'] = {}
                ticket['parent']['fields']['aggregateprogress']['percent'] = ''
                ticket['parent']['fields']['status'] = {}
                ticket['parent']['fields']['status']['name'] = ''

        return ticket


    def ticketsold(self, key=None, target='assignee'):
        """Lists all tickets for assigned to a user or project.

        :param key: Name of Jira user or project
        :param target: 'assignee' or 'project', default is 'assignee'
        """
        self.login()
        if not self.loggedin:
            return

        if key is None and target == 'assignee':
            key = self.user

        url = 'https://jira.esss.lu.se/rest/api/2/search?jql='+target+'=' + key + '&maxResults=999'
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response_ok = self.response_ok(response)
        if response_ok is False:
            return

        data = response.json()
        issues = data['issues']

        if not issues:
            W().write('No tickets found for \'{}\' \n' .format(key),'warning')
            return

        n = len(issues)
        tickets = []
        issue_types = []
        progress = []
        parent_keys = []
        summaries = []
        tree = []
        orphanage = ['Orphans', '', '', 'These children have no epic']
        has_orphanage = False

        # Find all parents
        for i in range(0, n):
            tickets.append(issues[i]['key'])
            issue_types.append(issues[i]['fields']['issuetype']['name'])
            s = issues[i]['fields']['summary']
            summaries.append(s[0:34]+'...' if len(s)>37 else s)

            try:
                p = str(issues[i]['fields']['aggregateprogress']['percent'])+'%'
            except Exception:
                p = 'None'

            progress.append(p)

            if issue_types[i] == "Epic":
                parent = [tickets[i], issue_types[i], progress[i], summaries[i]]
                parent_keys.append(tickets[i])
                tree.append((parent,[]))

        for i in range(0, n):
            if issue_types[i] == 'Sub-task':
                p = issues[i]['fields']['parent']
                t = p['fields']['issuetype']['name']
                s = p['fields']['summary']
                parent_key = issues[i]['fields']['parent']['key']
                if parent_key not in parent_keys:
                    parent = [parent_key, t, '', s]
                    parent_keys.append(parent_key)
                    tree.append((parent,[]))
            else:
                parent_key = issues[i]['fields']['customfield_10008']
                if not has_orphanage:
                    has_orphanage = True
                    tree.append((orphanage,[]))


        # Set all children
        for i in range(0, n):
            parent_key = issues[i]['fields']['customfield_10008']
            if parent_key is None and issue_types[i] == 'Sub-task':
                parent_key = issues[i]['fields']['parent']['key']
            elif parent_key is None and issue_types[i] != 'Epic':
                parent_key = 'Orphans'

            for parent, children in tree:
                if parent[0] == parent_key:
                    children.append(
                        [tickets[i], issue_types[i], progress[i], summaries[i]])

        # Print headers
        W().write('{:<16s}{:<15s}{:<10s}{}\n' .format('Ticket',
                                                  'Type',
                                                  'Progress',
                                                  'Summary'), 'header')
        # Print tree
        for parent, children in tree:
            W().write('{:<18s}{:<15s}{:<10s}{}\n' .format(parent[0],
                                                        parent[1],
                                                        parent[2],
                                                        parent[3]), 'epic')

            for child in children:
                W().write('   {:<15s}{:<15s}{:<10s}{}\n' .format(child[0],
                                                            child[1],
                                                            child[2],
                                                            child[3]), 'task')
        return tickets, issue_types, summaries, progress

    def assign(self, ticket, user):
        """Assign an issue to a user.

        param ticket: Jira issue.
        param user: The issue assigne to be set.
        """
        self.login()
        if not self.loggedin:
            return

        url = 'https://jira.esss.lu.se/rest/api/2/issue/'+ticket
        payload = '{"fields":{"assignee":{"name":"'+user+'"}}}'
        response = requests.put(
            url, auth=self.auth, headers=self.headers, data=payload)

        # Jira seems to return a bad json formatted string and the package
        # 'requests' throws an exception. Until that is fixed, this will be
        # caught and handled by the exception below.
        try:
            self.response_ok(response, ticket)
        except json.decoder.JSONDecodeError as e:
            s = str(response).split(']>')
            s = s[0].split('[')
            response_code = int(s[1])

            if response_code == 204:
                W().write('{} assigned to {}\n'
                               .format(ticket, user), 'ok')

    def org(self, path):
        """ parse emacs org-mode file with clock table and send work to Jira.

        :param path: Path to .org file
        """
        path = os.path.expanduser(path)

        if not os.path.exists(path):
            W().write('File \'{}\' does not exist\n' .format(path), 'warning')
            return

        with open(path) as f:
            lines = f.readlines()

        match_flag = False

        tickets = []
        times = []
        comments = []
        i = 0
        while True:
            if "#+END: clocktable" in lines[i]:
                break

            match = re.search("^\|[^-][^ Headline][^ \*Total].*ICSHWI", lines[i])
            if match is not None:
                match_flag = True
                cols = lines[i].split('|')
                tickets.append(re.search("ICSHWI(-\d+)?", cols[1]).group(0))
                comments.append(cols[-2].replace('"', '\\"'))
                time_list = re.search("\d*d* \d+:\d+", lines[i]).group(0)
                time_list = re.split(':|d ', time_list)

                if len(time_list) > 2:
                    times.append('{}d {}h {}m' .format(
                        time_list[0], time_list[1], time_list[1]))
                else:
                    times.append('{}h {}m' .format(time_list[0], time_list[1]))

                W().write('{}\t{}\t{}\n'
                              .format(tickets[-1], times[-1], comments[-1]))

            i += 1

        if match_flag:
            log = input('Would you like to log this? [Y/n]: ').lower()
            if log == "y":
                self.login()
                if not self.loggedin:
                    return
                for i in range(len(tickets)):
                    W().write('\n{}\t{}\t{}\n'
                                  .format(tickets[i], times[i], comments[i]))
                    self.log(tickets[i], times[i], comments[i])
            else:
                return
        else:
            W().write('No work to log found in {}\n' .format(path), 'warning')

    def projects(self):
        self.login()
        if not self.loggedin:
            return
        project_url = 'https://jira.esss.lu.se/rest/api/2/project'
        response = requests.get(project_url, auth=self.auth, headers=self.headers)
        response_ok = self.response_ok(response)
        if not response_ok:
            return
        data = response.json()
        for d in data:
            W().write("{:<15s}{:<65}\n" .format(d["key"], d["name"]))

    def getIssues(self, target_type, target, max_results=100, start=None, end=None):
        accepted = ["assignee", "project"]
        if target_type not in accepted:
            W().write("Invalid target type: {}" .format(target_type), "warning")

        url = "https://jira.esss.lu.se/rest/api/2/search?jql={}={}+order+by+updated&maxResults={}&expand=changelog" .format(target_type, target, max_results)

        response = requests.get(url, auth=self.auth, headers=self.headers)

        response_ok = self.response_ok(response)
        if not response_ok:
            return

        data = response.json()

        if start is None and end is None:
            return data["issues"]
        elif start is not None and end is not None:
            issues = []
            for i in data["issues"]:
                updated = i["fields"]["updated"]
                date = " ".join(re.split("T|\+", updated)[0:2])
                date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
                if start <= date_obj <= end:
                    issues.append(i)
            return issues
        else:
            W().write("Must use either both start and end times, or neither",
                          "warning")

    def getImplemented(self, issues):
        implemented = {}
        for i in issues:
            histories = i["changelog"]["histories"]
            for h in histories:
                items = h["items"]
                for item in items:
                    from_unimplemented = item["fromString"] != "Implemented"
                    to_implemented = item["toString"] == "Implemented"
                    if from_unimplemented and to_implemented:
                        implemented = self.updateDict(implemented, i, h["author"]["displayName"])

        return implemented

    def getWorklog(self, issues, start, end):
        work = {}
        for i in issues:
            url = 'https://jira.esss.lu.se/rest/api/2/issue/{}/worklog' \
              .format(i["key"])

            response = requests.get(url, auth=self.auth, headers=self.headers)
            log_data = response.json()
            worklogs = log_data["worklogs"]
            for w in worklogs:
                updated = w["updated"]
                date = " ".join(re.split("T|\+", updated)[0:2])
                date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')

                if start < date_obj < end:
                    comment = w["comment"].strip()
                    if comment:
                        work = self.updateDict(work, i, None, comment)
                    else:
                        work = self.updateDict(work, i, None)

        return work

    def updateDict(self, d, issue, author, comment=None):
        project = issue["fields"]["project"]["key"]
        if project not in d:
            d[project] = {}

        if issue["fields"]["assignee"] is not None:
            responsible = issue["fields"]["assignee"]["displayName"]
        else:
            responsible = author

        if responsible not in d[project]:
            d[project][responsible] = {}

        try:
            parent = issue["fields"]["parent"]
            parent_key = parent["key"]
            parent_summary = parent["fields"]["summary"]
        except:
            parent_key = None

        if parent_key not in d[project][responsible]:
            d[project][responsible][parent_key] = {}

        d_parent = d[project][responsible][parent_key]
        if parent_key is not None:
            d_parent["summary"] = parent["fields"]["summary"]
            d_parent["url"] = "https://jira.esss.lu.se/browse/{}" \
              .format(parent_key)

        if "children" not in d[project][responsible][parent_key]:
            d_parent["children"] = {}

        key = issue["key"]
        if key not in d_parent["children"]:
            d_parent["children"][key] = {}

        d_key = d_parent["children"][key]
        d_key["summary"] = issue["fields"]["summary"]
        d_key["url"] = "https://jira.esss.lu.se/browse/{}" .format(key)
        if comment is not None:
            if "comments" in d_key:
                d_key["comments"] = "{} | {}" .format(d_key["comments"], comment)
            else:
                d_key["comments"] = comment
        else:
            d_key["comments"] = ""

        return d

    def achievements(self, d):
        aments = []
        for p in d.keys(): # Project
            aments.append('<li>{}</li><ul>' .format(p))
            for r in d[p].keys(): # Responsible
                aments.append('<li>{}</li><ul>' .format(r))
                for parent, p_data in d[p][r].items(): # Parent
                    if parent is None:
                        real_parent = False
                        for o in p_data["children"].keys(): # Orphans
                            orphan = p_data["children"][o]
                            aments.append('<li>{}{} [<a href="{}">{}</a>]</li>'
                                            .format(orphan["summary"],
                                                    orphan["comments"],
                                                    orphan["url"], o))

                    else:
                        aments.append('<li>{} [<a href="{}">{}</a>]</li><ul>'
                                            .format(p_data["summary"],
                                                        p_data["url"],
                                                        parent))
                        real_parent = True

                    for key, data in d[p][r][parent]["children"].items(): # Key
                        if real_parent:
                            aments.append('<li>{}{} [<a href="{}">{}</a>]</li>'
                                            .format(data["summary"],
                                                    data["comments"],
                                                    data["url"], key))

                    if real_parent:
                        aments[-1] += "</ul>" # Close keys

                aments[-1] += "</ul>" # Close parents

            aments[-1] += "</ul>" # Close responsibles
        aments[-1] += "</ul>" # Close projects
        aments[-1] += "</ul>" # Close achievements

        # If report only regards user, remove project and responsible
        projects = list(d.keys())
        responsibles = list(d[projects[0]])
        if len(projects) == 1 and len(responsibles) == 1:
            user = "".join(responsibles[0].lower().split())
            if user == self.user:
                aments = aments[2:]
                aments[-1] = aments[-1][:-15]

        return aments

    def email(self, recipient, subject, body, html=False):
        self.login()
        if not self.loggedin:
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.mailaddress
        msg['To'] = recipient

        if html:
            body = MIMEText(body, 'html')

        msg.attach(body)

        try:
            server = smtplib.SMTP('mail.esss.lu.se', 587)
            server.starttls()
            server.login(self.user, self.auth[1])
            server.sendmail(self.mailaddress, recipient, msg.as_string())
            server.close()
            W().write('\nCheck your email ;)\n', 'ok')
        except:
            W().write('Failed to send  mail\n', 'warning')

    def getProjects(self):
        self.login()
        if not self.loggedin:
            return
        projects = []
        project_url = 'https://jira.esss.lu.se/rest/api/2/project'
        response = requests.get(project_url, auth=self.auth, headers=self.headers)
        data = response.json()
        for d in data:
            projects.append(d["key"])

        return projects

    def report(self, target_type, target, report_type, start, end, max_results,
                   planned_keys=None, problems=None):

        if target.lower() == "all":
            projects = self.getProjects()
            issues = []
            for project in projects:
                p = "'{}'" .format(project)
                issues += self.getIssues("project", p, max_results, start, end)
        else:
            issues = self.getIssues(target_type, target, max_results, start, end)

        if report_type == "implemented":
            report = self.getImplemented(issues)
        elif report_type == "worklog":
            report = self.getWorklog(issues, start, end)
        else:
            W().write("Invalid report type: {}\n" .format(report_type), "warning")
            return

        aments = self.achievements(report)
        mail = "<html>"
        mail += '<p>Dear {},</p>' .format(self.lm_mailaddress.split(".")[0].title())

        if target.lower() == "all":
            greeting = "ESS achievements:"
        elif target_type.lower() == "project":
            greeting = "{} achievements:" .format(target)
        else:
            greeting = "Achievements:"

        mail += "<p>{}</p>" .format(greeting)
        mail += "<ul>"
        for a in aments:
            mail += a

        if problems is not None:
            mail += '</ul>'
            mail += '<p>Issues:</p>'
            mail += '<ul>'
            problems = problems.split("| ")
            for p in problems:
                mail += '<li>{}</li>'.format(p)

        if planned_keys is not None:
            plans = self.getPlans(planned_keys)
            mail += '</ul>'
            mail += '<p>Plans for next week:</p>'
            mail += '<ul>'
            for p in plans:
                mail += p

        mail += "</ul>"

        mail += '<p>Cheers,<br />'
        mail += self.mailaddress.split(".")[0].capitalize()
        mail += '</p>'
        mail += '<p>&nbsp;</p>'
        mail += '<p>(This is an automatic message generated by Hermes)</p>'
        mail += '</html>'

        self.email(self.mailaddress, "Weekly report", mail, html=True)

    def getPlans(self, planned_keys):
        d = {}
        plans = []
        for key in planned_keys.split():
            url = 'https://jira.esss.lu.se/rest/api/2/issue/{}' .format(key)
            response = requests.get(url, auth=self.auth, headers=self.headers)
            if not self.response_ok(response, key):
                return

            issue = response.json()

            d = self.updateDict(d, issue, self.user)

        plans = self.achievements(d) #TODO: change name of def achievements
        # plans[-1] = plans[-1][:-10]

        return plans

    def weekly(self, target_type, target, report_type="implemented",
                   planned_keys=None, problems=None):
        self.login()
        if not self.loggedin:
            return
        today = datetime.today()
        start = today - timedelta(days=today.weekday())
        start = datetime.combine(start, datetime.min.time())
        end = start + timedelta(days=6)
        end = datetime.combine(end, datetime.max.time())

        if target_type == "assignee":
            max_results = 50
        elif report_type == "implemented":
            max_results = 150
        else:
            max_results = 300

        self.report(target_type, target, report_type, start, end, max_results,
                        planned_keys, problems)

    def stop_loading(self):
        self.stop = True
        time.sleep(0.3)

    def loading(self):
        load_char = '|'
        while True:
            if load_char == '|':
                load_char = '/'
            elif load_char == '/':
                load_char = '-'
            elif load_char == '-':
                load_char = '\\'
            elif load_char == '\\':
                load_char = '/'
            elif load_char == '/':
                load_char = '|'
            W().write('\r{}' .format(load_char), 'task')
            sys.stdout.flush()
            if self.stop == True:
                self.stop = False
                sys.stdout.flush()
                break
            time.sleep(0.15)

    def graph(self, ticket, shape='box'):
        self.login()
        if not self.loggedin:
            return

        t = threading.Thread(target=self.loading)
        t.daemon = False
        t.start()

        path = os.path.dirname(os.path.abspath(__file__)) # Path to hermes dir
        options = {
            'cookie' : None,
            'jira_url' : 'https://jira.esss.lu.se',
            'image_file' : path + '/' + ticket + '_graph.png',
            'store_true' : False,
            'store_true' : False,
            'excludes' : [],
            'closed' : False,
            'includes' : '',
            'show_directions' : ['inward', 'outward'],
            'directions' : ['inward', 'outward'],
            'node_shape' : shape,
            'store_true' : False,
            'traverse' : True,
            'word_wrap' : False,
            'no_verify_ssl' : False,
            'ignore_epic' : False,
            'ignore_subtasks' : False,
            'local' : False,
            }

        jira = JiraSearch(options['jira_url'],
                              self.auth,
                              options['no_verify_ssl'])

        try:
            graph = jira.build_graph_data(ticket,
                                          jira,
                                          options['excludes'],
                                          options['show_directions'],
                                          options['directions'],
                                          options['includes'],
                                          options['closed'],
                                          options['ignore_epic'],
                                          options['ignore_subtasks'],
                                          options['traverse'],
                                          options['word_wrap'])
        except requests.exceptions.HTTPError:
            W().write('Dang, something went wrong\n', 'warning')
            self.stop_loading()
            return None

        if options['local']:
            # jira.print_graph(jira.filter_duplicates(graph),
            #                      options['node_shape'])
            jira.print_graph(graph, options['node_shape'])
        else:
            # jira.create_graph_image(jira.filter_duplicates(graph),
            #                        options['image_file'],
            #                        options['node_shape'])
            jira.create_graph_image(graph,
                                        options['image_file'],
                                        options['node_shape'])

        self.stop_loading()
        W().write('Saved image to {}\n'
                          .format(options['image_file']), 'ok')

        imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
        # subprocess.run([imageViewerFromCommandLine, options['image_file']])
        return options['image_file']
