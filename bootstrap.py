'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from subprocess import Popen, PIPE, check_output
from libam.config import Config

def services_on():
    ambot_path = Config.get('AMBOT_PATH')
    Popen(['%sjava.exe' % ambot_path, '-jar', '%sselenium-server.jar' % ambot_path], stdout=PIPE)

def services_off():
    Popen(['taskkill', '/F', '/IM', 'java.exe'])
    Popen(['taskkill', '/F', '/IM', 'chromedriver.exe'])
