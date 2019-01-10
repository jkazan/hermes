from __future__ import print_function
import signal
import os
import shlex
from terminal import Write, Color
from jira import HJira
from install import HInstall

class CLIReactor(object):
    """Hermes Command Line Interface."""

    def __init__(self):
        """Initialization."""
        self.event_loop_active = True
        self.hjira = HJira()
        self.hinstall = HInstall()

    def run(self):
        """Run script."""
        self.help()

        while self.event_loop_active:
            prompt_color = Write.colors['prompt'].readline_escape
            prompt = "{} >> ".format(prompt_color('Hermes'))

            try:
                self.dataReceived(input(prompt))
            except EOFError:
                Write().write("\n")
                return
            except KeyboardInterrupt:
                Write().write("\n")
                pass

    def quit(self):
        """Quit CLI."""
        self.event_loop_active = False
        os.kill(os.getpid(), signal.SIGINT)

    def help(self):
        """Print help text."""
        assign_descr = 'Assign an issue to a user'
        help_descr = 'List commands (show this message)'
        comment_descr = 'Comment on a tickets e.g. "comment"'
        comments_descr = 'Get all comments on a ticket'
        graph_descr = 'Draw ticket relationship graph'
        log_descr = 'Log work, e.g. log "3h 20m" "comment"'
        org_descr = 'Parse emacs org-mode file and log work'
        quit_descr = 'Quit Hermes'
        tickets_a_descr = 'List assignee\'s tickets'
        tickets_p_descr = 'List project\'s tickets'
        username_descr = 'Remember or forget username'
        install_e3 = 'Install e3 with epics 7 + common mods'
        install_css = 'Install css production|development'
        install_plcf = 'Install plc factory'
        install_beast = 'Install BEAST alarm handler'

        help_text = {
            # name                                      function
            'Hermes'                                  : None,
            'help'                                    : help_descr,
            'quit'                                    : quit_descr,
            'Jira'                                    : None,
            'assign    <ticket> <assignee>'           : assign_descr,
            'comment   <ticket> "<comment>"'          : comment_descr,
            'comments  <ticket>'                      : comments_descr,
            'graph     <ticket>'                      : graph_descr,
            'log       <ticket> "<time>" "<comment>"' : log_descr,
            'org       <path>'                        : org_descr,
            'tickets   [<assignee>]'                  : tickets_a_descr,
            '          [<project> project]'           : tickets_p_descr,
            'username  remember | forget'             : username_descr,
            'Installation'                            : None,
            'install   e3 <install path>'             : install_e3,
            '          css <install path> [<branch>]' : install_css,
            '          plcfactory <install path>'     : install_plcf,
            '          beast <install path>'          : install_beast,
            }

        title = "Commands:"
        # Find longest command in order to make list as compact as possible
        cols = max(len(max(help_text.keys(), key=lambda x: len(x))), len(title))

        Write().write('{} {} Description:'
                       .format(title, " "*(cols - len(title))), "header")

        commands = help_text.keys()

        for cmd in commands:
            spacing = " "*(cols - len(cmd))
            if help_text[cmd] is None:
                Write().write('\n({})\n' .format(cmd), 'task')
            else:
                Write().write("%s %s %s\n"
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
            # name           function
            # HERMES ######################
            "help"          : self.help,
            "quit"          : self.quit,
            # JIRA ########################
            "assign"        : self.hjira.assign,
            "comment"       : self.hjira.comment,
            "comments"      : self.hjira.comments,
            "graph"         : self.hjira.graph,
            "log"           : self.hjira.log,
            "org"           : self.hjira.org,
            "tickets"       : self.hjira.tickets,
            "username"      : self.hjira.username,
            # INSTALL #####################
            "install"       : self.hinstall.install,
            }

        # Check if we have a valid command
        if command not in commands:
            Write().write("Invalid command '{}'\n" .format(command), "warning")
            Write().write("Type 'help' to see all commands\n")
            return

        function = commands[command]

        try:
            args = self.parse(data)
            function(*args)
        except TypeError as type_error:
            Write().write("{}\n".format(type_error), "warning")

    def parse(self, args, comments=False, posix=True):
        """Parse command from command line.

        :param args: Command line arguments
        :param comments: shlex parameter
        :param posix: shlex parameter

        :returns: Split arguments
        """
        slit_args = shlex.split(args, comments, posix)
        return slit_args

if __name__ == '__main__':
    reactor = CLIReactor()
    reactor.run()
