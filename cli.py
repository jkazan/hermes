from __future__ import print_function
import sys
import signal
import os
import readline
import shlex
import json
from terminal_colors import Color
import requests

class CLIReactor(object):
    colors = {
        'regular'  : Color(),
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

        :param sci_client: The SCI client.
        """
        self.event_loop_active = True
        self.headers = {'Content-Type': 'application/json',}
        self.user = user
        self.auth = (user, passwd)

    def run(self):
        self.cliHelp()
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
        sys.stdout.write(self.colors[color](string))

    def cliComment(self, ticket, comment):
        """Comment on a Jira ticket.

        param ticket: Jira ticket key.
        param comment: Comment to post to ticket.
        """
        url = 'https://jira.esss.lu.se/rest/api/latest/issue/'+ticket+'/comment'
        payload = '{"body":"'+comment+'"}'
        response = requests.post(
            url, auth=self.auth, headers=self.headers, data=payload)
        self.parse_response(response, ticket)

    def cliLog(self, ticket, time, comment):
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

    def parse_response(self, response, ticket):
        data = response.json()

        if response.status_code == 201:
            self.write('Successfully posted\n', 'ok')
        elif response.status_code == 400:
            errorMessages = data['errorMessages'][0]
            errors = data['errors']['timeLogged']
            self.write('{} {}\n' .format(errorMessages, errors), 'warning')
        elif response.status_code == 404:
            errorMessages = data['errorMessages'][0]
            self.write('{}\n' .format(errorMessages), 'warning')

    def cliGetTickets(self, user=None):
        """Lists all tickets for assigned to user."""
        if user is None:
            user = self.user

        url = 'https://jira.esss.lu.se/rest/api/2/search?jql=assignee=' + user
        response = requests.get(url, auth=self.auth, headers=self.headers)
        data = response.json()
        issues = data['issues']
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
                    # print('{}' .format(progress[i]))
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

    def cliQuit(self):
        """Quit CLI."""
        self.event_loop_active = False
        os.kill(os.getpid(), signal.SIGINT)

    def cliHelp(self):
        """Print help text."""
        help_descr = 'List valid commands'
        comment_descr = 'Comment on a tickets (comment in quotes).'
        log_descr = 'Log work, e.g. log "3h 20m" "comment"'
        quit_descr = 'Quit Jira CLI'
        tickets_descr = 'List assignee\'s tickets.'

        help_text = {
            'help'                              : help_descr,
            'comment <ticket> "<comment>"'      : comment_descr,
            'log <ticket> "<time>" "<comment>"' : log_descr,
            'quit'                              : quit_descr,
            'tickets [<assignee>]'              : tickets_descr,
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
            # name            function
            "help"          : self.cliHelp,
            "comment"       : self.cliComment,
            "log"           : self.cliLog,
            "quit"          : self.cliQuit,
            "tickets"       : self.cliGetTickets,
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
        except Exception as e:
            self.write("{}\n".format(e), "warning")

    def parse(self, args, comments=False, posix=True):
        test = shlex.split(args, comments, posix)
        return test


if __name__ == '__main__':
    import getpass
    user = input("Jira username: ")
    passwd = getpass.getpass("Password: ")

    reactor = CLIReactor(user, passwd)
    reactor.run()
