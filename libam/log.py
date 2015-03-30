'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from Tkinter import INSERT, END
import logging

class Log(object):
    def __init__(self, out_win, path):
        self.current_line = 1
        self.out_win = out_win

        self.logger = logging.getLogger('amazon_robot')
        hdlr = logging.FileHandler('%s\\assets\\robot.log' % path)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)
        self.color_codes = {
            "error": "red",
            "info": "blue",
            "warning": "yellow"
        }

    def write(self, level, out):
        self.out_win.insert(INSERT, "[%s] - %s\n" % (level, out))
        self.out_win.tag_add("%d"   % self.current_line,
                             "%d.0" % self.current_line,
                             "%d.%d" % (self.current_line, len(level)+2))
        self.out_win.tag_config("%d" % self.current_line,
                                background="black",
                                foreground=self.color_codes[level])
        getattr(self.logger, level)(out)
        self.current_line += 1
        self.out_win.yview(END)

    def clear(self):
        pass
