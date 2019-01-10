from __future__ import print_function
import os
import readline
import json
from terminal import Write
import requests
import getpass
import inspect
import re

class HJira(object):

    def __init__(self):
        self.user = None
        self.auth = (self.user, None)
        self.headers = {'Content-Type': 'application/json',}

    def jiraLogin(self):
        """" Login to Jira account. """
        user_file = 'jira.user'
        script_file = os.path.basename(__file__)
        path = os.path.dirname(os.path.abspath(__file__))

        if self.user is not None:
            return

        if os.path.isfile(path+'/'+user_file):
            with open(path+'/'+user_file, 'r') as f:
                json_data = json.load(f)
                self.user = json_data['user']
        else:
            self.user = input("Jira username: ")

        password = getpass.getpass("Password: ")
        self.auth = (self.user, password)

        #TODO: verify self.auth
        # login_ok = False
        # while not login_ok:
        #     password = getpass.getpass("Password: ")
        #     self.auth = (self.user, password)
        #     try:
        #         url = 'https://jira.esss.lu.se/rest/api/2/search?jql=assignee=' + self.user
        #         response = requests.get(url, auth=self.auth, headers=self.headers)
        #         # response_ok = self.response_ok(response)
        #         login_ok = True
        #     except Exception:
        #         Write().write('try again\n', 'warning')


    def username(self, action):
        """Settings for logged in user.

        Username can be stored in local file, or removed from
        it. Remembering the username will enable logging into Jira using
        password only.

        param action: 'remember' or 'forget' username
        """
        path = os.path.dirname(os.path.abspath(__file__))
        user_file = 'jira_cli.user'

        if action == 'remember':
            if os.path.isfile(path+'/'+user_file):
                Write().write('{} is already remembered\n'
                               .format(self.user), 'warning')
            else:
                with open(path+'/'+user_file, 'a') as f:
                    f.write('{"user":"'+user+'"}')
                    Write().write('{} will be remembered\n' .format(self.user), 'ok')
        elif action == 'forget':
            if os.path.isfile(path+'/'+user_file):
                os.remove(path+'/'+user_file)
                Write().write('{} has been forgotten\n' .format(self.user), 'ok')
            else:
                Write().write('{} was not known\n' .format(self.user), 'warning')
        else:
            Write().write('Invalid action \'{}\'\n' .format(action), 'warning')


    def comment(self, ticket, comment):
        """Comment on a Jira ticket.

        param ticket: Jira ticket key.
        param comment: Comment to post to ticket.
        """
        self.jiraLogin()

        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'+ticket+'/comment'
        payload = '{"body":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload)
        self.response_ok(response, ticket)

    def comments(self, ticket):
        """Get comments on a Jira ticket.

        param ticket: Jira ticket key.
        """
        self.jiraLogin()

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
            Write().write('{}:{}' .format(names[i], spacing), color)

            line_len = max_len + 1
            col_nbr = 0
            for k in range(len(comments[i])):
                col_nbr += 1
                if line_len + col_nbr == int(cols):
                    col_nbr = 0
                    Write().write('\n{}' .format(" "*(max_len+1)))
                    if comments[i][k] == ' ':
                        continue

                Write().write('{}' .format(comments[i][k]), color)
            print('')

    def log(self, ticket, time, comment):
        """Log work.

        param ticket: Jira ticket key.
        param time: Time spent to post to ticket's work log..
        param comment: Comment to post to ticket's work log.
        """
        self.jiraLogin()

        url = 'https://jira.esss.lu.se/rest/api/2/issue/'+ticket+'/worklog'
        payload = '{"timeSpent":"'+time+'","comment":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload)
        self.response_ok(response, ticket)

    def response_ok(self, response, ticket=None):
        """Parse Jira response message

        :param response: Jira response message
        :param ticket: Jira ticket

        :returns: True if request was successful, False otherwise
        """
        data = response.json()
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]

        if response.status_code == 200:
            return True # Successful 'get'
        elif response.status_code == 201:
            Write().write('Successfully posted\n', 'ok')
            return True
        elif response.status_code == 400:
            if data['errorMessages']:
                errorMessages = data['errorMessages'][0]
                Write().write('{}\n' .format(errorMessages), 'warning')

            if caller == 'assign':
                errors = data['errors']['assignee']
                Write().write('{}\n' .format(errors), 'warning')
            elif caller == 'log':
                errors = data['errors']['timeLogged']
                Write().write('{}\n' .format(errors), 'warning')

        elif response.status_code == 404:
            errorMessages = data['errorMessages'][0]
            Write().write('{}\n' .format(errorMessages), 'warning')

        return False

    def tickets(self, key=None, target='assignee'):
        """Lists all tickets for assigned to a user or project.

        :param key: Name of Jira user or project
        :param target: 'assignee' or 'project', default is 'assignee'
        """
        self.jiraLogin()

        if key is None and target == 'assignee':
            key = self.user

        url = 'https://jira.esss.lu.se/rest/api/2/search?jql='+target+'=' + key
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response_ok = self.response_ok(response)

        if response_ok is False:
            return

        data = response.json()
        issues = data['issues']

        if not issues:
            Write().write('No tickets found for \'{}\' \n' .format(key),'warning')
            return

        n = len(issues)
        tickets = []
        issue_types = []
        progress = []
        parent_keys = []
        summaries = []
        tree = []
        orphanage = ['Orphans', 'None', 'None', 'These children have no epic']
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
                parent_key = issues[i]['fields']['parent']['key']
                if parent_key not in parent_keys:
                    parent = [parent_key, 'Unknown', 'Unknown', 'Unknown']
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
        Write().write('{:<18s}{:<15s}{:<10s}{}\n' .format('Ticket',
                                                  'Type',
                                                  'Progress',
                                                  'Summary'), 'header')
        # Print tree
        for parent, children in tree:
            Write().write('{:<18s}{:<15s}{:<10s}{}\n' .format(parent[0],
                                                        parent[1],
                                                        parent[2],
                                                        parent[3]), 'epic')

            for child in children:
                Write().write('   {:<15s}{:<15s}{:<10s}{}\n' .format(child[0],
                                                            child[1],
                                                            child[2],
                                                            child[3]), 'task')


    def assign(self, ticket, user):
        """Assign an issue to a user.

        param ticket: Jira issue.
        param user: The issue assigne to be set.
        """
        self.jiraLogin()

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
                Write().write('{} assigned to {}\n'
                               .format(ticket, user), 'ok')


    def org(self, path):
        """ parse emacs org-mode file with clock table and send work to Jira.

        :param path: Path to .org file
        """
        path = os.path.expanduser(path)

        if not os.path.exists(path):
            Write().write('File \'{}\' does not exist\n' .format(path), 'warning')
            return

        with open(path) as f:
            lines = f.readlines()

        match_flag = False

        tickets = []
        times = []
        comments = []
        for i in range(0,len(lines)):
            match = re.search("^\|[^-][^ Headline][^ \*Total].*ICSHWI", lines[i])
            if match is not None:
                match_flag = True
                cols = lines[i].split('|')
                tickets.append(re.search("ICSHWI(-\d+)?", cols[1]).group(0))
                comments.append(cols[5])
                time_list = re.search("\d+:\d+", lines[i]).group(0).split(':')
                times.append('{}h {}m' .format(time_list[0], time_list[1]))
                Write().write('{}\t{}\t{}\n' .format(tickets[-1], times[-1], comments[-1]))

        if match_flag:
            log = input('Would you like to log this? [Y/n]: ').lower()
            if log == "y":
                self.jiraLogin()
                for i in range(len(tickets)):
                    Write().write('\n{}\t{}\t{}\n' .format(tickets[i], times[i], comments[i]))
                    self.log(tickets[i], times[i], comments[i])
            else:
                return
        else:
            Write().write('No work to log found in {}\n' .format(path), 'warning')
