from __future__ import print_function
import signal
import os
import shlex
from terminal import Write
from jira import HJira
from install import HInstall
from difflib import get_close_matches

try:
    import readline
except ImportError:
    import pyreadline as readline


class CLIReactor(object):
    """Hermes Command Line Interface."""

    def __init__(self):
        """Initialization."""
        self.event_loop_active = True
        self.hjira = HJira()
        self.hinstall = HInstall()
        self.history = os.path.dirname(os.path.abspath(__file__)) + "/.hermes_history"
        readline.read_history_file(self.history)
        self.commands = {
            # name           function
            # HERMES ######################
            "help": self.help,
            "quit": self.quit,
            "email": self.hjira.email,
            # JIRA ########################
            "assign": self.hjira.assign,
            "comment": self.hjira.comment,
            "comments": self.hjira.comments,
            # "estimate"      : self.hjira.estimate,
            "graph": self.hjira.graph,
            "log": self.hjira.log,
            "org": self.hjira.org,
            "projects": self.hjira.projects,
            "state": self.hjira.state,
            "subtask": self.hjira.subtask,
            "task": self.hjira.task,
            "tickets": self.hjira.tickets,
            "report": self.hjira.report,
            "forgetme": self.hjira.forgetme,
            # INSTALL #####################
            "install": self.hinstall.install,
        }

    def completer(self, text, state):  # TODO: move to terminal.py
        options = [i for i in self.commands if i.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    def run(self):
        """Run script."""
        self.help()

        while self.event_loop_active:
            prompt_color = Write.colors["prompt"].readline_escape
            prompt = "{} >> ".format(prompt_color("Hermes"))
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.completer)

            try:
                self.dataReceived(input(prompt))
            except EOFError:
                Write().write("\n")
                return
            except KeyboardInterrupt:
                self.hjira.stop_loading()  # If jira is loading, stop it
                Write().write("\n")
                pass

    def quit(self):
        """Quit CLI."""
        self.event_loop_active = False
        os.kill(os.getpid(), signal.SIGINT)

    def help(self):
        """Print help text."""
        help_text = {
            # name                                      function
            "Hermes": None,
            "email     <to> <subject> <message>": "Send email",
            "help": "List commands (show this message)",
            "quit": "Quit Hermes",
            "Jira": None,
            "assign    <ticket> <assignee>": "Assign an issue to a user",
            'comment   <ticket> "<comment>"': "Comment on a ticket",
            "comments  <ticket>": "Get all comments on a ticket",
            # 'estimate  <ticket> "<time>"'             : estimate_descr,
            "graph     <ticket> links|subtasks|all": "Draw relationship graph",
            "          [<path to save graph>]": "Default is current path",
            'log       <ticket> "<time>" "<comment>"': "Log work to a ticket",
            "org       <path to .org file>": "Parse emacs org-mode file and log work",
            "projects": "Get a list of all Jira projects",
            'state     <ticket> "<state>"': "Change state of ticket, e.g. backlog",
            'subtask   <parent> "<title>" "<effort>"': "Create subtask related to its parent",
            "task      <summary> [<description>]": "Create task",
            "tickets   [<assignee>]": "List assignee's tickets",
            "          [<project> project]": "List project's tickets",
            "forgetme": "Delete user data",
            "report    [OPTION]...": "Send report email to user, examples:",
            "          project=<project>|all": "report project=ICSHWI",
            "          assignee=<username>": "report assignee=johnsmith",
            "          type=implemented|worklog": "report type=worklog",
            '          plans="<ticket> <ticket>..."': 'report plans="ICSWHI-1650"',
            '          problems="<p1> | <p2>..."': 'report problems="This | That"',
            '          dates="<from> <to>"': 'report dates="2019-08-01 2019-08-10"',
            "Installation": None,
            "install   e3 <install path>": "Install e3 with epics 7 + common mods",
            "          archiver <install path>": "Install archiver appliance",
            "          css <install path> [<branch>]": "Install css production|development",
            "          plcfactory <install path>": "Install plc factory",
            "          beast <install path>": "Install BEAST alarm handler",
            "          phoebus <install path> <java>": "Install Phoebus",
        }

        title = "Commands:"
        # Find longest command in order to make list as compact as possible
        cols = max(len(max(help_text.keys(), key=lambda x: len(x))), len(title))

        Write().write(
            "{} {} Description:".format(title, " " * (cols - len(title))), "header"
        )

        commands = help_text.keys()

        for cmd in commands:
            spacing = " " * (cols - len(cmd))
            if help_text[cmd] is None:
                Write().write("\n({})\n".format(cmd), "task")
            else:
                Write().write("%s %s %s\n" % (cmd, spacing, help_text[cmd]))

    def dataReceived(self, data):
        """Handles request from the command line.

        param data: Input data from command line.
        """
        # Split command from argument and strip from whitespace etc.
        data = data.strip()
        command, _, data = data.partition(" ")
        data = data.strip()

        # Check if the request is empty
        if not command:
            return

        # Check if we have a valid command
        if command not in self.commands:
            Write().write("Invalid command '{}'. ".format(command), "warning")
            Write().write("Type 'help' to see all commands\n")
            notrealword = get_close_matches(command, self.commands, n=5, cutoff=0.6)
            if notrealword:
                print("Perhaps you mean:")
                for n in notrealword:
                    print(n)

            return

        function = self.commands[command]

        try:
            args = self.parse(data)
            function(*args)
            with open(self.history, "a") as f:
                f.write(command + "\n")
        except TypeError as type_error:
            Write().write("{}\n".format(type_error), "warning")

    def parse(self, args, comments=False, posix=True):
        """Parse command from command line.

        :param args: Command line arguments
        :param comments: shlex parameter
        :param posix: shlex parameter

        :returns: Split arguments
        """
        split_args = shlex.split(args, comments, posix)
        return split_args


if __name__ == "__main__":
    reactor = CLIReactor()
    reactor.run()
