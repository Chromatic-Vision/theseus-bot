from datetime import datetime

import os
import io
import traceback

class Logger:

    def __init__(self, colored: bool, write_to_file: bool, format: str, color_mappings=None, filename="latest.log"):
        if color_mappings is None:
            color_mappings = [
                "\033[34m", # 0, timestamp
                "\033[36m", # 1, traceback
                "\033[32m", # info
                "\033[33m", # warn
                "\033[31m" # error
            ]
        self.colored = colored
        self.write_to_file = write_to_file
        self.format = format
        self.color_mappings = color_mappings
        self.filename = filename

    def log(self, message):
        print(self.parse(self.format, message, self.colored, 0))

        if self.write_to_file:
            self.write(self.parse(self.format, message, False, 0))

    def warn(self, message):
        print(self.parse(self.format, message, self.colored, 1))

        if self.write_to_file:
            self.write(self.parse(self.format, message, False, 1))

    def error(self, message):
        print(self.parse(self.format, message, self.colored, 2))

        if self.write_to_file:
            self.write(self.parse(self.format, message, False, 2))

    def write(self, content):
        with open(self.filename, 'a', encoding="UTF-8") as f:
            f.write(content + "\n")
            f.close()

    def reset_log(self):

        if not self.write_to_file:
            return

        if self.filename not in os.listdir('.'):
            with open(self.filename, 'w', encoding="UTF-8") as f:
                f.close()
                return

        with open(self.filename, 'w', encoding="UTF-8") as f:
            f.truncate()
            f.close()

    def parse(self, format: str, message: str, colors: bool, type: int):

        if type > 2:
            raise ValueError(f"Unknown type: {type}")

        res = ""

        if colors:
            res += "\033[0m" # reset all colors, if needed

        res += datetime.now().strftime(format)
        res = res.replace("$info", self.info_from_type(type)) # string based on type, e.g. WARN, ERROR...

        if colors:
            res = res.replace("$reset", "\033[0m")  # reset color
            res = res.replace("$color", self.color_mappings[type + 2]) # color based on type, e.g. "\033[33m" (represents yellow), here its +2 because indexes 0, 1 is used for other color
            res = res.replace("$timecolor", self.color_mappings[0])
            res = res.replace("$tracecolor", self.color_mappings[1])
        else:
            res = res.replace("$color", "")
            res = res.replace("$reset", "")
            res = res.replace("$timecolor", "")
            res = res.replace("$tracecolor", "")

        res = res.replace("$filename", self.trace()[0]) # filename of function
        res = res.replace("$funcname", self.trace()[1]) # name of function
        res = res.replace("$line", self.trace()[2]) # line of function
        res = res.replace("$message", message) # message

        return res

    def trace(self) -> tuple:

        _filename = None
        _func = None
        _line = None

        trace = io.StringIO()
        traceback.print_stack(file=trace)
        trace_string = trace.getvalue()
        trace.close()
        trace_string_formatted = ''
        space = False
        even = True
        for c in trace_string:
            if c == '\n':
                if not even:
                    trace_string_formatted += ';'
                    even = True
                else:
                    even = False

                trace_string_formatted += ' '
                space = True
            elif c == ' ':
                pass
            else:
                space = False

            if not space:
                trace_string_formatted += c
                # print(trace_string_formatted)

        filenames = ''
        filename = ''
        state = 0
        line = ''
        i = 0
        while i < len(trace_string_formatted):
            c = trace_string_formatted[i]

            if state == 0:
                if c == '"':
                    state = 1
            elif state == 1:
                if c != '"':
                    filename += c
                else:
                    filenames += os.path.basename(filename)
                    filename = ''
                    state = 2

            elif state == 2:

                j = i + 7

                while j < len(trace_string_formatted) and trace_string_formatted[j] != ',':
                    line += trace_string_formatted[j]

                    j += 1

                state = 3
                i = j

            elif state == 3:
                j = i + 4
                # print("call")
                func = ''
                while j < len(trace_string_formatted) and trace_string_formatted[j] != ' ':
                    func += trace_string_formatted[j]
                    # print(func)
                    j += 1
                state = 4

                _func = func
                _line = line
                filenames += " "
                line = ''
            elif state == 4:
                if trace_string_formatted[i] == ';':  # TODO: you can't have a semicolon in the python
                    state = 0

            i += 1

        file_traces = filenames[:-1].split(" ")
        first_file = str(file_traces[-4])

        _filename = first_file.replace('.py', '')

        return _filename, _func, _line

    def info_from_type(self, type: int):
        if type == 0:
            return "INFO"
        elif type == 1:
            return "WARN"
        elif type == 2:
            return "ERROR"
        else:
            return "INVALID"