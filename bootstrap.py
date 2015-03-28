'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from subprocess import Popen, PIPE, check_output
from libam.config import Config

def selenium_server_on(conf):
    root = conf.get('root_path')
    #Popen(['%sjava.exe' % root, '-jar', '%sselenium-server.jar' % root], stdout=PIPE)

def selenium_server_off():
    #Popen(['taskkill', '/F', '/IM', 'java.exe'])
    try:
        Popen(['taskkill', '/F', '/IM', 'chromedriver.exe'])
    except:
        pass

def check_dependencies():
    pass