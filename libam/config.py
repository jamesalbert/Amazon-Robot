'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from yaml import load, dump
from os import environ

class Config(object):
    def __init__(self):
        with open('%s\\AmazonRobot\\assets\\conf.yaml' % environ['LOCALAPPDATA']) as config:
            self.conf = load(config)
        config.close()

    def get(self, key):
        val = self.conf.get(key)
        if isinstance(val, list):
            result = {}
            for e in val:
                result.update(e)
            return result
        return self.conf.get(key) or str()

    def get_all(self):
        return self.conf

    def set(self, key, val):
        self.conf[key] = val
        with open('%s\\AmazonRobot\\assets\\conf.yaml' % environ['LOCALAPPDATA'], 'w+') as new_config:
            new_config.write(dump(self.conf, indent=2))
        new_config.close()