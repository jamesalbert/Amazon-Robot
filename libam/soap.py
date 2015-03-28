'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from suds.client import Client
from config import Config


class Service(object):
    '''
    Soap service handler for getting and updating orders
    '''
    def __init__(self):
        '''
        establishes connection with soap api
        :return:
        '''
        self.conf = Config()
        self.url = self.conf.get('service_url')
        self.user_id = 'jalbert' or self.conf.get('service_user_id')
        self.password = 'cobb45cent8' or self.conf.get('service_password')
        self.cli = Client(self.url)

    def get_order(self, id):
        '''
        get order information
        :param id: int
        :return:
        '''
        res = self.cli.service.GetOrderSelenium(
            iOrderID=id,
            sUserID=self.user_id,
            sPassword=self.password
        )
        return dict(res)

    def set_order(self, lg_id, order_id, sales_tax, unit_price):
        '''
        set/update order information
        :param lg_id: int
        :param order_id: string
        :param sales_tax: decimal
        :param unit_price: decimal
        :return:
        '''
        res = self.cli.service.UpdateOrderSelenium(
            iOrderID=lg_id,
            sAmazonOrderID=order_id,
            decAmazonSalesTax=sales_tax,
            decAmazonUnitPrice=unit_price,
            sUserID=self.user_id,
            sPassword=self.password
        )
        return res