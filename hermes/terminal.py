import os
import sys


class Color(object):
    def __init__(self):
        self.codes = []
        self.do_readline_escape = False

    def copy(self):
        obj = self.__class__()
        obj.codes = list(self.codes)
        obj.do_readline_escape = self.do_readline_escape
        return obj

    def code(code):
        def append(self):
            newcolor = self.copy()
            newcolor.codes.append(code)
            return newcolor

        return property(append)

    bold = code("1")
    faint = code("2")

    black = code("30")
    red = code("31")
    green = code("32")
    yellow = code("33")
    blue = code("34")
    magenta = code("35")
    cyan = code("36")
    white = code("37")

    bright_blue = code("94")

    @property
    def readline_escape(self):
        newcolor = self.copy()
        newcolor.do_readline_escape = True
        return newcolor

    def perform_escape(self, string):
        if self.do_readline_escape:
            return "\x01" + string + "\x02"
        else:
            return string

    def __call__(self, string):
        if string:
            return "{}{}{}".format(
                self.perform_escape("\x1b[" + ";".join(self.codes) + "m"),
                string,
                self.perform_escape("\x1b[0m"),
            )
        else:
            return string


class Write(object):
    colors = {
        "regular": Color(),
        "prompt": Color().bright_blue,
        "header": Color().bold.white,
        "warning": Color().red,
        "task": Color().cyan,
        "epic": Color().magenta,
        "ok": Color().green,
        "tip": Color().yellow,
    }

    def write(self, string, color="regular"):
        """Print method with custom colors.

        :param string: String to print
        :param color: Font color, default is 'regular'
        """
        if os.name == "nt":
            sys.stdout.write(str(string))
        else:
            sys.stdout.write(self.colors[color](str(string)))
