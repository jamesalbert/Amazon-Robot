'''
 * Copyright (C) James Robert Albert III - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by James Albert <jamesrobertalbert@gmail.com>, March 2015
'''

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import select
from selenium.webdriver.common.keys import Keys
from soap import Service
import time

class Amazon(object):
    def __init__(self, app):
        '''
        Amazon class

        contains functions for logging in, adding
        contacts, and purchase items.
        '''
        '''grab config file, setup logging'''
        self.conf = app.conf
        self.log = app.log
        self.case = None
        self.current_row = None

        '''urls'''
        self.root = self.conf.get('root_path')
        self.login_url = self.conf.get("login_url")
        self.product_url = self.conf.get('product_url')
        self.cart_url = self.conf.get('cart_url')
        self.new_address_url = self.conf.get('new_address_url')
        self.manage_address_url = self.conf.get('manage_address_url')
        self.shipping_url = self.conf.get('shipping_url')
        self.payment_url = self.conf.get('payment_url')
        self.buy_url = self.conf.get('buy_url')
        self.orders_url = self.conf.get('orders_url')
        self.ambot_path = self.conf.get('AMBOT_PATH')
        self.lg_id = self.conf.get('LG Order #')

        '''user information'''
        prefs = self.conf.get('preferences')
        self.email = prefs['email']
        self.password = prefs['password']

        '''start selenium'''
        self.driver = webdriver.Chrome('%s\\assets\\chromedriver.exe' % self.ambot_path)


    def login(self):
        '''
        login to Amazon
        '''

        '''login'''
        self.log.write('info', 'logging in')
        self.driver.get(self.login_url)
        email_input = self.driver.find_element_by_name('email')
        passw_input = self.driver.find_element_by_name('password')
        email_input.send_keys(self.email)
        passw_input.send_keys(self.password + Keys.ENTER)
        try:
            time.sleep(5)
            self.driver.find_element_by_xpath('//*[@id="ap_signin1a_pagelet_title"]/h1')
            self.log.write('error', 'wrong username or password')
            self.driver.close()
            return False
        except:
            self.log.write('info', 'logged in successfully')
            return True

    def safely_quit(self, message, clear_cart=False):
        name = self.case.get('Ship To Name')
        self.log.write('error', message)
        self.delete_address(name)
        if clear_cart:
            self.clear_cart()

    def buy_product(self):
        self.log.write('info', 'attempting to purchase item')
        asin = self.case.get('Product ASIN')
        quantity = self.case.get('Qty').strip('.0')
        product_url = '%s%s' % (self.product_url, asin)
        self.driver.get(product_url)

        '''check if product is an add-on item'''
        try:
            self.driver.find_element_by_xpath('//span[contains(text(), "Add-on Item")]')
            self.safely_quit('product is an addon item, cannot be bought')
            return
        except:
            '''product is a go for buying'''
            pass

        '''quantity'''
        s = self.driver.find_element_by_name('quantity')
        try:
            select.Select(s).select_by_value(quantity)
        except:
            self.safely_quit("quantity is set too high, please review the spreadsheet")
            return
        time.sleep(2)

        '''get product description'''
        '''
        #desc_frame = self.driver.find_element_by_id('product-description-iframe')
        #self.driver.switch_to.frame(desc_frame)
        #desc = self.driver.find_element_by_class_name('productDescriptionWrapper').text
        #self.driver.switch_to.default_content()
        desc = self.driver.find_element_by_id('productTitle').text
        '''

        '''get unit price'''
        unit_price = self.driver.find_element_by_id('priceblock_ourprice').text

        '''add to cart'''
        self.driver.find_element_by_name('submit.add-to-cart').click()
        time.sleep(2)

        '''say no to warranties'''
        try:
            no_thanks = self.driver.find_element_by_id('siNoCoverage-announce')
            no_thanks.click()
        except Exception as e:
            '''no warranty offered'''
            pass

        time.sleep(2)
        self.driver.get(self.cart_url)
        self.log.write('info', 'item added to cart')

        '''this is a gift'''
        time.sleep(2)
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'This is a gift')]").click()
        except:
            self.log.write('warning', 'gift options not available')

        '''shipping'''
        time.sleep(2)
        self.driver.get(self.shipping_url)
        try:
            shipping_xpath = '//a[contains(@class, "checkout-continue-link") and contains(text(), "Ship to this address")]'
            self.driver.find_elements_by_xpath(shipping_xpath)[-1].click()
        except:
            shipping_xpath = '//a[contains(@class, "a-declarative") and contains(text(), "Ship to this address")]'
            self.driver.find_elements_by_xpath(shipping_xpath)[-1].click()

        '''payment'''
        time.sleep(5)
        self.driver.get(self.payment_url)
        gc = self.driver.find_element_by_id('pm_gc_checkbox')
        if not gc.is_selected():
            '''choose gift card if not selected'''
            gc.click()
        try:
            total = int(self.driver.find_element_by_xpath('//*[@id="subtotals-marketplace-table"]/table/tbody/tr[9]/td[2]') \
                            .text.split('$')[1])
            if total > 0:
                self.safely_quit('Insufficient funds', clear_cart=True)
        except:
            button = self.driver.find_element_by_xpath('//*[@id="continue-top"]')
            hover = ActionChains(self.driver).move_to_element(button)
            hover.perform()
            if button.is_displayed():
                button.click()
            else:
                self.safely_quit('Insufficient funds', clear_cart=True)
                return False

        '''place order'''
        time.sleep(5)
        self.driver.get(self.buy_url)
        if self.driver.find_element_by_name('placeYourOrder1').is_displayed():
            amazon_tax_xpath = '//td[contains(text(), "$") and ancestor::tr[descendant::td[contains(text(), "Estimated tax to be collected")]]]'
            amazon_tax = self.driver.find_element_by_xpath(amazon_tax_xpath).text
            self.driver.find_element_by_name('placeYourOrder1').click()
            self.log.write('info', 'item purchased')
            self.delete_address(self.case.get('Ship To'))
            order_id = self.get_orderid()
            try:
                Service().set_order(
                    self.lg_id,
                    order_id,
                    amazon_tax,
                    unit_price
                )
            except Exception as e:
                print e.message
        return True

    def add_address(self):
        '''
        add address to Amazon account
        '''
        self.driver.get(self.new_address_url)

        '''fill out new address form'''
        for field, name in self.conf.get('address').iteritems():
            element = self.driver.find_element_by_name(name)
            element.send_keys(self.case.get(field) or ' ')

        '''turn on weekend shipping'''
        weekend = self.driver.find_element_by_name('AddressType')
        weekend.click()
        for opt in weekend.find_elements_by_tag_name('option'):
            if 'Yes' in opt.text:
                opt.click()
        self.driver.find_element_by_name('newAddress').click()

        '''keep original address'''
        try:
            keep_address = self.driver.find_element_by_name('addr')
            save_button = self.driver.find_element_by_name('useSelectedAddress')
            keep_address.click()
            save_button.click()
        except Exception as e:
            '''no address was suggested'''
            pass
        self.log.write('info', 'address added')

    def add_card(self, **kwargs):
        pass

    def get_orderid(self):
        '''grab order ID from orders page'''
        self.driver.get(self.orders_url)
        time.sleep(5)
        order_id_xpath = '//*[@id="ordersContainer"]/div[2]/div[1]/div/div/div/div[2]/div[1]/span[2]'
        order_id = self.driver.find_element_by_xpath(order_id_xpath).text
        return order_id

    def start_orders(self, cases):
        '''start ordering products'''
        self.log.write('info', 'fulfilling orders')
        for i, case in enumerate(cases):
            if not case.get('LG Order #'):
                self.log.write('warning', 'reached end of .xlsx or lg order # omitted')
                break
            self.case = case
            self.current_row = i + 2
            self.add_address()
            self.buy_product()
        self.log.write('info', 'orders automation completed')
        self.driver.close()

    def delete_address(self, name):
        full_address_xpath = 'td[descendant::b[contains(text(), "%s")]]' % name
        delete_xpath = '//span[contains(text(), "Delete") and ancestor::%s]' % full_address_xpath
        self.driver.get(self.manage_address_url)
        self.driver.find_element_by_xpath(delete_xpath).click()
        self.driver.find_element_by_xpath('//span[contains(text(), "Confirm")]').click()
        self.log.write('info', 'address deleted')

    def clear_cart(self):
        self.driver.get(self.cart_url)
        items = self.driver.find_elements_by_xpath('//input[contains(@value, "Delete")]')
        for item in items:
            item.click()
        self.log.write('info', 'cart cleared')
