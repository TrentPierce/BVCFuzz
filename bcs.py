import re
import sys
import json
import signal
import requests
import cssutils
import threading

from cssutils import css
from BeautifulSoup import BeautifulSoup


def signal_handler(signal, frame):
    global page

    sys.stdout.write("Finished on page: %d\n" % page)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class WalletThread(threading.Thread):
    def __init__(self, url):
        self.url = url
        threading.Thread.__init__ (self)

    def run(self):
        global processes

        processes += 1

        subreq = requests.get(self.url)

        if str(subreq.status_code) == '200':
            balance = BeautifulSoup(subreq.text).find('td', id = 'total_received')
            value = float(balance.text.strip('BTC'))
            print str(wallet_key) + '; ' + str(wallet_rsa) + '; ' + str(wallet_url) + "\n"

            if value > 0:
                print str(wallet_key) + '; ' + str(wallet_rsa) + '; ' + str(wallet_url) + "\n"
                
                    

        processes -= 1


page = 0


url = 'http://directory.io/'
status = None
processes = 0

while status != '404':
    page += 1

    sys.stdout.write("\rPage: %d, processes run: %d" % (page, processes))
    sys.stdout.flush()
    
    req = requests.post(url + str(page))

    if str(req.status_code) != '404':
        wallet_key = None
        wallet_rsa = None
        wallet_url = None

        soup = BeautifulSoup(req.text)
        keys = soup.find('pre', {'class' : 'keys'})

        for strong in keys.findAll('strong'):
            strong.decompose()

        for wallet in str(keys).split("\n"):

            w_soup = BeautifulSoup(wallet)

            for plus in w_soup.findAll('a', href = re.compile(r'warning')):
                plus.decompose()

            for block in w_soup:
                if type(block).__name__ == 'NavigableString':
                    wallet_rsa = block.string.strip()

                if type(block).__name__ == 'Tag':
                    wallet_url = block.get('href')
                    wallet_key = block.text

            

            if wallet_url:
                WalletThread(str(wallet_url)).start()
