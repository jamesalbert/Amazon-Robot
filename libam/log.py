'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from Tkinter import INSERT, END

class Log(object):
    def __init__(self, out_win):
        self.current_line = 1
        self.out_win = out_win

        self.color_codes = {
            "error": "red",
            "info": "blue",
            "warn": "yellow"
        }

    def write(self, level, out):
        self.out_win.insert(INSERT, "[%s] - %s\n" % (level, out))
        self.out_win.tag_add("%d"   % self.current_line,
                             "%d.0" % self.current_line,
                             "%d.7" % self.current_line)
        self.out_win.tag_config("%d" % self.current_line,
                                background="black",
                                foreground=self.color_codes[level])
        self.current_line += 1
        self.out_win.yview(END)

    def clear(self):
        pass
