from __future__ import print_function
import sys
import signal
import os
import readline
import shlex
import json
from terminal_colors import Color
import requests
import getpass
import inspect

class CLIReactor(object):
    colors = {
        'regular' : Color(),
        'prompt'  : Color().bright_blue,
        'header'  : Color().bold.white,
        'warning' : Color().red,
        'list1'   : Color(),
        'list2'   : Color().faint,
        'task'    : Color().cyan,
        'epic'    : Color().magenta,
        'orphan'  : Color(),
        'ok'      : Color().green,
    }

    def __init__(self, user, passwd):
        """Initialization.

        :param user: Jira username
        :param passwd: Jira password
        """
        self.event_loop_active = True
        self.headers = {'Content-Type': 'application/json',}
        self.user = user
        self.auth = (user, passwd)

    def run(self):
        self.help()
        self.parse('ICSHWI-711 "1h 20m" "This is my comment"')

        while self.event_loop_active:
            prompt_color = self.colors['prompt'].readline_escape
            prompt = "{} >> ".format(prompt_color('jira'))

            try:
                self.dataReceived(input(prompt))
            except EOFError:
                self.write("\n")
                return
            except KeyboardInterrupt:
                self.write("\n")
                pass

    def write(self, string, color="regular"):
        """Print method with custom colors.

        :param string: String to print
        :param color: Font color, default is 'regular'
        """
        sys.stdout.write(self.colors[color](string))

    def comment(self, ticket, comment):
        """Comment on a Jira ticket.

        param ticket: Jira ticket key.
        param comment: Comment to post to ticket.
        """
        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'+ticket+'/comment'
        payload = '{"body":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload)
        self.parse_response(response, ticket)

    def log(self, ticket, time, comment):
        """Log work.

        param ticket: Jira ticket key.
        param time: Time spent to post to ticket's work log..
        param comment: Comment to post to ticket's work log.
        """
        url = 'https://jira.esss.lu.se/rest/api/2/issue/'+ticket+'/worklog'
        payload = '{"timeSpent":"'+time+'","comment":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload)
        self.parse_response(response, ticket)

    def parse_response(self, response, ticket=None):
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
            self.write('Successfully posted\n', 'ok')
            return True
        elif response.status_code == 400:
            if data['errorMessages']:
                errorMessages = data['errorMessages'][0]
                self.write('{}\n' .format(errorMessages), 'warning')

            if caller == 'assign':
                errors = data['errors']['assignee']
                self.write('{}\n' .format(errors), 'warning')
            elif caller == 'log':
                errors = data['errors']['timeLogged']
                self.write('{}\n' .format(errors), 'warning')

        elif response.status_code == 404:
            errorMessages = data['errorMessages'][0]
            self.write('{}\n' .format(errorMessages), 'warning')

        return False

    def tickets(self, key=None, target='assignee'):
        """Lists all tickets for assigned to user.

        :param user: Jira assignee
        """
        if key is None and target == 'assignee':
            key = self.user

        url = 'https://jira.esss.lu.se/rest/api/2/search?jql='+target+'=' + key
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response_ok = self.parse_response(response)

        if response_ok is False:
            return

        data = response.json()
        issues = data['issues']

        if not issues:
            self.write('No tickets found for \'{}\' \n' .format(key),'warning')
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
        self.write('{:<18s}{:<15s}{:<10s}{}\n' .format('Ticket',
                                                  'Type',
                                                  'Progress',
                                                  'Summary'), 'header')
        # Print tree
        for parent, children in tree:
            self.write('{:<18s}{:<15s}{:<10s}{}\n' .format(parent[0],
                                                        parent[1],
                                                        parent[2],
                                                        parent[3]), 'epic')

            for child in children:
                self.write('   {:<15s}{:<15s}{:<10s}{}\n' .format(child[0],
                                                            child[1],
                                                            child[2],
                                                            child[3]), 'task')

    def quit(self):
        """Quit CLI."""
        self.event_loop_active = False
        os.kill(os.getpid(), signal.SIGINT)

    def forget(self):
        """Forget logged in user."""
        path = os.path.dirname(os.path.abspath(__file__))
        user_file = 'jira_cli.user'
        if os.path.isfile(path+'/'+user_file):
            os.remove(path+'/'+user_file)
            self.write('{} has been forgotten\n' .format(self.user), 'ok')
        else:
            self.write('{} was not known\n' .format(self.user), 'warning')

    def help(self):
        """Print help text."""
        assign_descr = 'Assign an issue to a user.'
        forget_descr = 'Forget logged in user.'
        help_descr = 'List valid commands'
        comment_descr = 'Comment on a tickets e.g. "comment".'
        log_descr = 'Log work, e.g. log "3h 20m" "comment".'
        quit_descr = 'Quit Jira CLI.'
        tickets_descr = 'List assignee\'s tickets.'

        help_text = {
            # name                                       function
            'assign <ticket> <assignee>'               : assign_descr,
            'help'                                     : help_descr,
            'forget'                                   : forget_descr,
            'comment <ticket> "<comment>"'             : comment_descr,
            'log <ticket> "<time>" "<comment>"'        : log_descr,
            'quit'                                     : quit_descr,
            'tickets [<assignee> | <project> project]' : tickets_descr,
            }

        title = "Command:"

        # Find longest command in order to make list as compact as possible
        cols = max(len(max(help_text.keys(), key=lambda x: len(x))), len(title))

        self.write("%s %s Description:\n"
                       %(title, " "*(cols - len(title))), "header")

        commands = help_text.keys()

        for cmd in commands:
            spacing = " "*(cols - len(cmd))
            self.write("%s %s %s\n"
                           %(cmd, spacing, help_text[cmd]))

    def assign(self, ticket, user):
        """Assign an issue to a user.

        param ticket: Jira issue.
        param user: The issue assigne to be set.
        """
        url = 'https://jira.esss.lu.se/rest/api/2/issue/'+ticket
        payload = '{"fields":{"assignee":{"name":"'+user+'"}}}'
        response = requests.put(
            url, auth=self.auth, headers=self.headers, data=payload)

        # Jira seems to return a bad json formatted string and the package
        # 'requests' throws an exception. Until that is fixed, this will be
        # caught and handled by the exception below.
        try:
            self.parse_response(response, ticket)
        except json.decoder.JSONDecodeError as e:
            s = str(response).split(']>')
            s = s[0].split('[')
            response_code = int(s[1])

            if response_code == 204:
                self.write('{} assigned to {}\n'
                               .format(ticket, user), 'ok')

    def dataReceived(self, data):
        """Handles request from the command line.

        param data: Input data from command line.
        """
        # Split command from argument and strip from whitespace etc.
        data = data.strip()
        command, _, data = data.partition(' ')
        data = data.strip()

        # Check if the request is empty
        if not command:
            return

        commands = {
            # name           function
            "assign"        : self.assign,
            "forget"        : self.forget,
            "help"          : self.help,
            "comment"       : self.comment,
            "log"           : self.log,
            "quit"          : self.quit,
            "tickets"       : self.tickets,
            }

        # Check if we have a valid command
        if command not in commands:
            self.write("Invalid command '{}'\n" .format(command), "warning")
            self.write("Type 'help' to see all commands\n")
            return

        function = commands[command]

        try:
            args = self.parse(data)
            function(*args)
        except TypeError as type_error:
            self.write("{}\n".format(type_error), "warning")

    def parse(self, args, comments=False, posix=True):
        test = shlex.split(args, comments, posix)
        return test


if __name__ == '__main__':
    user_file = 'jira_cli.user'
    script_file = os.path.basename(__file__)
    path = os.path.dirname(os.path.abspath(__file__))

    if os.path.isfile(path+'/'+user_file):
        with open(path+'/'+user_file, 'r') as f:
            json_data = json.load(f)
            user = json_data['user']

        passwd = getpass.getpass("Password: ")
    else:
        user = input("Jira username: ")
        passwd = getpass.getpass("Password: ")
        remember = input("Remember username? [y/n]: ")
        if remember == 'y':
            with open(path+'/'+user_file, 'a') as f:
                f.write('{"user":"'+user+'"}')

    reactor = CLIReactor(user, passwd)
    reactor.run()
