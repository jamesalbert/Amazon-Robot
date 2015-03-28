'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from libam.amazon import Amazon
from libam.config import Config
from libam.xls import Spreadsheet
from libam.log import Log
from libam.soap import Service
from os import environ

import Tkinter as tk, tkFileDialog, tkMessageBox
import pygubu, pygubu.builder.ttkstdwidgets, threading
import bootstrap

class Application:
    def __init__(self, master):
        '''
        creates main window, starts services like configuration and logging
        :param master: tk.TK
        :return:
        '''
        print "Ignore this prompt, it's needed for the browser to start"

        self.conf = Config()
        self.conf.set('AMBOT_PATH', '%s\\AmazonRobot' % environ['LOCALAPPDATA'])
        self.ambot_path = self.conf.get('AMBOT_PATH')

        t = threading.Thread(target=bootstrap.selenium_server_on, args=(self.conf,))
        t.start()

        self.builder = pygubu.Builder()
        self.builder.add_resource_path('%s\\assets' % self.ambot_path)
        self.builder.add_from_file('%s\\assets\\G.ui' % self.ambot_path)
        self.main = self.builder.get_object('Main', master)
        callbacks = {
            'browse': self.browse,
            'order': self.order
        }
        self.builder.connect_callbacks(callbacks)
        self.log = Log(self.get_output_window())
        self.log.write('info', 'Amazon Robot started')

    def check_user_cache(self):
        '''
        checks if required preferences are set
        :return:
        '''
        preferences = self.conf.get('preferences')
        required = ['email', 'password', 'sUserID', 'sPassword']
        for k, v in preferences.iteritems():
            if k in required and not v:
                tkMessageBox.showinfo('Reminder', 'Set all the required fields in File>Preferences')
                break

    def get_output_window(self):
        '''
        returns output window object
        :return:
        '''
        return self.builder.get_object('output')

    def browse(self):
        '''
        reads in a spreadsheet file, converts it to a dict,
        readies the script to order.
        :return:
        '''
        try:
            self.xlpath = tkFileDialog.askopenfile(mode='r').name
            if not self.xlpath.endswith('.xlsx'):
                raise IOError
            self.builder.get_variable('path').set(self.xlpath)
            self.builder.get_object('order')['state'] = 'normal'
        except AttributeError:
            '''the user closed it without choosing a file'''
            pass
        except IOError:
            tkMessageBox.showinfo('xlsx error', 'That is not an .xlsx file!')
            self.builder.get_object('order')['state'] = 'disabled'

    def order(self):
        '''
        loops through spreadsheet dict, carries out orders,
        sends back order data to the soap service
        :return:
        '''

        '''
        load up spreadsheet
        '''
        prefs = self.conf.get('preferences')
        if not prefs['email'] or not prefs['password']:
            self.log.write('error', 'must provide username and password in File>Preferences')
            return
        self.xl = Spreadsheet(self.xlpath)
        test_cases = self.xl.toDict()
        order_button = self.builder.get_object('order')
        order_button['state'] = 'disabled'
        '''
        load Amazon with Selenium
        '''

        def start_amazon():
            self.am = Amazon(self.conf, self.log)
            if self.am.login():
                try:
                    self.am.start_orders(test_cases)
                except Exception as e:
                    try:
                        self.log.write('error', e.msg[:15])
                    except:
                        self.log.write('error', e.message)
                    self.log.write('info', 'browser closed')

            order_button['state'] = 'normal'

        t = threading.Thread(target=start_amazon)
        t.start()

    def open_preferences(self):
        '''
        preferences window
        :return:
        '''
        new_win = tk.Toplevel(root)
        new_win.title('Preferences')
        new_win.focus_set()
        new_win.geometry('445x385')
        new_win.wm_iconbitmap(bitmap="%s\\assets\\amazon.ico" % self.ambot_path)

        '''
        create new build, load Preferences.ui
        '''
        builder = pygubu.Builder()
        builder.add_from_file('%s\\assets\\Preferences.ui' % self.ambot_path)
        pref_win = builder.get_object('Main', new_win)

        '''
        pull in saved values from conf.yaml
        '''

        def load_default(key):
            conf_val = self.conf.get('preferences')[key]
            builder.get_variable(key).set(conf_val)

        def set_defaults(keys):
            preferences = {}
            for key in keys:
                preferences[key] = builder.get_variable(key).get()
            self.conf.set('preferences', preferences)

        def save_preferences():
            '''
            save values to conf.yaml
            '''
            set_defaults(pref_fields)
            quit_win()

        def quit_win():
            '''
            callback for closing preferences
            '''
            new_win.destroy()
            pref_win.destroy()

        pref_fields = self.conf.get('preferences').keys()
        for field in pref_fields:
            load_default(field)

        callbacks = {
            'save_preferences': save_preferences
        }
        builder.connect_callbacks(callbacks)


if __name__ == '__main__':
    root = tk.Tk()

    '''
    toolbar settings
    '''
    root.wm_title("Amazon Robot")
    root.wm_iconbitmap(bitmap="%s\\AmazonRobot\\assets\\amazon.ico" % environ['LOCALAPPDATA'])

    '''
    app config
    '''

    app = Application(root)

    '''
    menu bar settings
    '''
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Preferences", command=app.open_preferences)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)
    app.check_user_cache()

    def close_services():
        bootstrap.selenium_server_off()
        root.quit()

    root.protocol('WM_DELETE_WINDOW', close_services)

    try:
        root.mainloop()
    except:
        bootstrap.selenium_server_off()