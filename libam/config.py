'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from yaml import load, dump
from os import environ

class Config(object):
    with open('%s\\AmazonRobot\\assets\\conf.yaml' % environ['LOCALAPPDATA']) as config:
        conf = load(config)
    config.close()

    @staticmethod
    def get(key):
        val = Config.conf.get(key)
        if isinstance(val, list):
            result = {}
            for e in val:
                result.update(e)
            return result
        return Config.conf.get(key) or str()

    @staticmethod
    def set(key, val):
        Config.conf[key] = val
        with open('%s\\AmazonRobot\\assets\\conf.yaml' % environ['LOCALAPPDATA'], 'w+') as new_config:
            new_config.write(dump(Config.conf, indent=2))
        new_config.close()