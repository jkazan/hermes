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
            W().write('Check your email ;)\n', 'ok')
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

    def getParent(self, ticket, summary=False):
        meta = 'https://jira.esss.lu.se/rest/api/2/issue/'+ticket
        response = requests.get(meta, auth=self.auth, headers=self.headers)
        response_ok = self.response_ok(response)
        if not response_ok:
            return False
        meta_data = response.json()
        try:
            parent = meta_data["fields"]["parent"]
            parent_key = parent["key"]
            parent_summary = parent["fields"]["summary"]
        except:
            parent_key = "orphan"
            parent_summary = ""

        if summary:
            return parent_key, parent_summary, meta_data["fields"]["summary"]
        else:
            return parent_key, parent_summary

    def weekly(self, trigger, planned_tickets=None, problems=None):
        trigger = trigger.upper()
        projects = ["HWI", "MPS", "INFR"]
        users = ["IMPLEMENTED", "WORKLOG"]
        if trigger not in projects and trigger not in users:
            W().write("Invalid trigger: '{}'\n" .format(trigger), "warning")
            return

        self.login()
        if not self.loggedin:
            return

        today = datetime.today()
        start = today - timedelta(days=today.weekday())
        start = datetime.combine(start, datetime.min.time())
        end = start + timedelta(days=6)
        end = datetime.combine(end, datetime.max.time())

        if trigger in projects:
            ticket_url = 'https://jira.esss.lu.se/rest/api/2/search?jql=project=ICS{}+order+by+updated&maxResults=50&expand=changelog' .format(trigger)
        else:
            ticket_url = 'https://jira.esss.lu.se/rest/api/2/search?jql=assignee={}+order+by+updated&maxResults=20&expand=changelog' .format(self.user)

        response = requests.get(ticket_url, auth=self.auth, headers=self.headers)
        response_ok = self.response_ok(response)
        if not response_ok:
            return

        data = response.json()
        issues = data['issues']

        if not issues:
            W().write("No tickets found \n", "warning")
            return

        report = {}
        for i in issues:
            comments = [""]
            updated = i["fields"]["updated"]
            date = " ".join(re.split("T|\+", updated)[0:2])
            date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
            has_work = False
            ticket = i["key"]

            if start < date_obj < end:
                if trigger == "WORKLOG":
                    log_url = 'https://jira.esss.lu.se/rest/api/2/issue/{}/worklog' .format(ticket)
                    response = requests.get(log_url, auth=self.auth, headers=self.headers)
                    response_ok = self.response_ok(response)
                    log_data = response.json()
                    worklogs = log_data["worklogs"]

                    for w in worklogs:
                        updated = w["updated"]
                        date = " ".join(re.split("T|\+", updated)[0:2])
                        date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')

                        if start < date_obj < end:
                            has_work = True
                            comments.append(w["comment"].strip().replace(".", ""))

                elif trigger == "IMPLEMENTED" or trigger in projects:
                    histories = i["changelog"]["histories"]
                    for h in histories:
                        items = h["items"]
                        for item in items:
                            from_unimplemented = item["fromString"] != "Implemented"
                            to_implemented = item["toString"] == "Implemented"
                            if from_unimplemented and to_implemented:
                                has_work = True
            else:
                break

            if has_work:
                user = i["fields"]["assignee"]["name"]
                if user not in list(report.keys()):
                    report[user] = {}

                parent_key, parent_summary = self.getParent(ticket)

                if parent_key not in list(report[user].keys()):
                    report[user][parent_key] = {}
                    report[user][parent_key]["description"] = parent_summary
                    report[user][parent_key]["children"] = {}

                report[user][parent_key]["children"][ticket] = {}
                report[user][parent_key]["children"][ticket]["description"] = i["fields"]["summary"]
                report[user][parent_key]["children"][ticket]["comment"] = comments

        # If a parent to a ticket is also in orphan, remove it from orphan
        for p in report:
            if "orphan" in report[user]:
                if p in report[user]["orphan"]["children"]:
                    report[user]["orphan"]["children"].pop(p, None)

        browse_url = 'https://jira.esss.lu.se/browse'

        if trigger in users:
            achievements = self.user_achievements(report, browse_url)
        else:
            achievements = self.project_achievements(report, browse_url)

        email = '<html>'
        email += '<p>Dear {},</p>' .format(self.lm_mailaddress.split(".")[0].title())

        if achievements:
            email += '<p>Achievements:</p>'
            email += '<ul>'

        for a in achievements:
            email += a

        if problems is not None:
            email += '</ul>'
            email += '<p>Issues:</p>'
            email += '<ul>'
            problems = problems.split("| ")
            for p in problems:
                email += '<li>{}</li>'.format(p)

        plans = {}
        if planned_tickets is not None:
            for ticket in planned_tickets.split():
                url = 'https://jira.esss.lu.se/rest/api/2/issue/{}' .format(ticket)
                data = self.getParent(ticket, True)

                if not data:
                    W().write("{}\n" .format(ticket), "warning")
                    continue
                else:
                    parent_key = data[0]
                    parent_summary = data[1]
                    summary = data[2]

                    if parent_key not in list(plans.keys()):
                        plans[parent_key] = {}
                        plans[parent_key]["description"] = parent_summary
                        plans[parent_key]["children"] = {}

                    plans[parent_key]["children"][ticket] = {}
                    plans[parent_key]["children"][ticket]["description"] = summary

            for p in plans:
                if "orphan" in plans and p in plans["orphan"]["children"]:
                    plans["orphan"]["children"].pop(p, None)

            plan_text = []
            for parent, parent_data in plans.items():
                if parent != "orphan":
                    plan_text.append('<li>{} [<a href="{}/{}">{}</a>]</li><ul>'
                                        .format(plans[parent]["description"],
                                                    browse_url, parent, parent))

                for ticket, data in plans[parent]["children"].items():
                    plan_text.append('<li>{} [<a href="{}/{}">{}</a>]</li>'
                                        .format(data["description"],
                                                browse_url, ticket, ticket))

                if parent != "orphan":
                    last_entry = plan_text[-1] + "</ul>"
                    plan_text[-1] = last_entry

            email += '</ul>'
            email += '<p>Plans for next week:</p>'
            email += '<ul>'
            for p in plan_text:
                email += p

        email += '</ul>'
        email += '<p>Cheers,<br />'
        email += self.mailaddress.split(".")[0].capitalize()
        email += '</p>'
        email += '<p>&nbsp;</p>'
        email += '<p>(This is an automatic message generated by Hermes)</p>'
        email += '</html>'

        self.email(self.mailaddress, "Weekly report", email, html=True)

    def user_achievements(self, report, browse_url):
        achievements = []
        for parent, parent_data in report[self.user].items():
            if parent != "orphan":
                achievements.append('<li>{} [<a href="{}/{}">{}</a>]</li><ul>'
                                        .format(report[self.user][parent]["description"],
                                                    browse_url, parent, parent))

            for ticket, data in report[self.user][parent]["children"].items():
                comment = ""
                for c in data["comment"]:
                    if c.strip():
                        comment += c.strip().replace(".", "")+". "
                if comment:
                    comment = ": " + comment

                achievements.append('<li>{}{} [<a href="{}/{}">{}</a>]</li>'
                                        .format(data["description"],
                                                comment,
                                                browse_url, ticket, ticket))

            if parent != "orphan":
                last_entry = achievements[-1] + "</ul>"
                achievements[-1] = last_entry

        return achievements

    def project_achievements(self, report, browse_url):
        achievements = []
        for u in report.keys():
            achievements.append('<li>{}</li><ul>' .format(u))
            for parent, parent_data in report[u].items():
                if parent != "orphan":
                    achievements.append('<li>{} [<a href="{}/{}">{}</a>]</li><ul>'
                                            .format(report[u][parent]["description"],
                                                        browse_url, parent, parent))

                for ticket, data in report[u][parent]["children"].items():
                    comment = ""
                    for c in data["comment"]:
                        if c.strip():
                            comment += c.strip().replace(".", "")+". "
                    if comment:
                        comment = ": " + comment

                    achievements.append('<li>{}{} [<a href="{}/{}">{}</a>]</li>'
                                            .format(data["description"],
                                                    comment,
                                                    browse_url, ticket, ticket))

                if parent != "orphan":
                    last_entry = achievements[-1] + "</ul>"
                    achievements[-1] = last_entry

            achievements[-1] = achievements[-1] + "</ul>"

        return achievements

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
            W().write('\rloading {}' .format(load_char), 'task')
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
