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
        self.conf = self.get_config()
        self.ambot_path = self.conf.get('AMBOT_PATH')
        self.manage_chromedriver()
        self.master = master
        self.builder = self.get_builder()
        self.log = self.get_logger()

    def get_logger(self):
        '''get logger object'''
        output_win = self.builder.get_object('output')
        log = Log(output_win, self.ambot_path)
        log.write('info', 'Amazon Robot started')
        return log

    def get_builder(self):
        '''get builder object'''
        builder = pygubu.Builder()
        builder.add_resource_path('%s\\assets' % self.ambot_path)
        builder.add_from_file('%s\\assets\\G.ui' % self.ambot_path)
        builder.get_object('Main', self.master)
        '''setup button callbacks'''
        callbacks = {
            'browse': self.browse,
            'order': self.order
        }
        builder.connect_callbacks(callbacks)
        return builder

    def get_config(self):
        '''get configuration object'''
        conf = Config()
        conf.set('AMBOT_PATH', '%s\\AmazonRobot' % environ['LOCALAPPDATA'])
        return conf

    def fields_satisfied(self):
        '''
        checks if required preferences are set
        :return:
        '''
        preferences = self.conf.get('preferences')
        required = ['email', 'password', 'sUserID', 'sPassword']
        for k, v in preferences.iteritems():
            if k in required and not v:
                tkMessageBox.showinfo('Reminder', 'Set all the required fields in File>Preferences')
                return False
        return True

    def set_order_button(self, state='normal'):
        '''used for enabling/disabling order button'''
        self.builder.get_object('order')['state'] = state

    def load_spreadsheet(self):
        file_obj = tkFileDialog.askopenfile(mode='r')
        if not hasattr(file_obj, 'name'):
            return True
        self.xl_path = file_obj.name
        return self.xl_path.endswith('.xlsx')

    def browse(self):
        '''
        reads in a spreadsheet file, converts it to a dict,
        readies the script to order.
        :return:
        '''
        if not self.load_spreadsheet():
            tkMessageBox.showinfo('xlsx error', 'That is not an .xlsx file!')
            self.set_order_button('disabled')
        else:
            self.builder.get_variable('path').set(self.xl_path)
            self.set_order_button('normal')

    def order(self):
        '''
        loops through spreadsheet dict, carries out orders,
        sends back order data to the soap service
        :return:
        '''

        if not self.fields_satisfied():
            return
        self.set_order_button('disabled')
        self.start_amazon_orders()

    def start_amazon(self):
        '''
        load Amazon with Selenium
        '''
        self.amazon = Amazon(self)
        test_cases = Spreadsheet(self.xl_path).toDict()
        if self.amazon.login():
            try:
                self.amazon.start_orders(test_cases)
            except:
                self.log.write('error', 'browser closed')
        self.set_order_button('normal')

    def run_thread(self, fn, args=()):
        t = threading.Thread(target=fn, args=args)
        t.start()

    def manage_chromedriver(self):
        '''manage chromedriver process'''
        self.run_thread(bootstrap.selenium_server_on, (self.conf,))

    def start_amazon_orders(self):
        self.run_thread(self.start_amazon)

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
    app.fields_satisfied()

    def close_services():
        bootstrap.services_off()
        root.quit()

    root.protocol('WM_DELETE_WINDOW', close_services)

    try:
        root.mainloop()
    except:
        bootstrap.services_off()