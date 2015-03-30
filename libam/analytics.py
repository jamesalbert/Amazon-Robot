from config import Config
import requests

def update_usage():
    '''
    get 'http://relurk.com/usage'
    :return:
    '''
    url = Config.conf['usage_url']
    requests.get(url)