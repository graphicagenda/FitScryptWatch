import os
import requests
import json
import sqlite3
from datetime import datetime
from collections import namedtuple 
from notifypy import Notify
# TODO from pycoingecko import CoinGeckoAPI

__location = os.getcwd()
notification = Notify(
    custom_mac_notificator="./resource/FIT/FitScrypt Alerts.app"
)

'''
FitScrypt Home: https://fitscrypt.com
BSCScan Token Tracker: https://bscscan.com/token/0x24aa6a92be9d1c1cac5b625e650bb2b974eee16c
$FIT Dextools: https://www.dextools.io/app/bsc/pair-explorer/0xc209db0c4dd4eb1495dd8714302328bc8a760be2
'''


Langfile = namedtuple('Langfile', ['which', 'head', 'agent', 'action', 'perform'])
Token = namedtuple('Token', ['name', 'decimals', 'contract', 'uniswap'])
Network = namedtuple('Network', ['name', 'latestblock'])
API = namedtuple('API', ['token'])


class FITToken:
    def __init__(self, start_block=14176196):
        # @TODO CG: cg = CoinGeckoAPI()
        self.contract = '0x24aa6A92BE9d1C1cac5b625e650BB2b974eeE16c'
        self.lp_address = '0xc209db0c4dd4eb1495dd8714302328bc8a760be2'
        self.supply = 100000000000
        self.decimals = 9
        self.start_block = start_block
        self.end_block = 99999999
        self.api_key = os.environ['bscscan_api_key']
        self.url = self.bscscan_endpoint()
        # TODO Get more than just the newest set of last_tx and reverse it!
        self.data = self.request_data(self.url)
        if len(self.data) >= 1:
            self.last_tx = self.data[0]

        # @TODO CG: get_token_price = cg_endpoint()
        # @TODO CG: cg = get_token_price[CONTRACT]

    @staticmethod
    def request_data(url):
        r = requests.post(
            url,
            headers={"Content-Type": "application/json"},
        )

        return json.loads(r.text)['result']

    def bscscan_endpoint(self):
        return f"https://api.bscscan.com/api?module=account&" \
              f"action=tokentx&" \
              f"contractaddress={self.contract}&" \
              f"sort=desc&page=1&" \
              f"apikey={self.api_key}&" \
              f"startblock={self.start_block}&" \
              f"endblock={self.end_block}&" \
              f"page=1"


class Transaction:
    def __init__(self, bscscan_data, lp_address):
        self.eth_block = int(bscscan_data['blockNumber'])
        self.dt = get_formatted_time(int(bscscan_data['timeStamp']))

        self.__buy_lang = Langfile('buy', 'BUY!!!', bscscan_data['to'], 'Purchased', 'Received')
        self.__sell_lang = Langfile('sell', 'Sell :(', bscscan_data['from'], 'Sold', 'Sent')
        self.__transfer_lang = Langfile('transfer', 'Transfer', bscscan_data['from'], 'Sent', 'Moved')

        self.lang = {'buy': self.get_buy_lang(), 'sell': self.get_sell_lang(), 'transfer': self.get_transfer_lang()}

        self.trigger = get_trigger(bscscan_data['from'], bscscan_data['to'], lp_address, self.lang)
        self.wallet_address = bscscan_data['from'] if self.trigger == self.lang['sell'] else bscscan_data['to']

        self.raw_value = int(int(bscscan_data['value']) * (.1 ** int(bscscan_data['tokenDecimal'])))
        self.raw_full_amount = self.raw_value / .89

        self.FIT_amount = "{:,}".format(self.raw_value)
        self.full_FIT_amount = "{:,}".format(int(self.raw_full_amount))
        # @TODO CG: full_IT_amount_usd = f"${'{:,.0f}'.format(raw_full_amount * float(cg_data['usd']))}"

        # IT_Quotes
        # @TODO CG: quote = f"${'{:.5f}'.format(cg_data['usd'])}"
        # @TODO CG: vol = f"${'{:,.0f}'.format(cg_data['usd_24h_vol'])}"
        # @TODO CG: mc = f"${'{:,.0f}'.format(cg_data['usd'] * int(SUPPLY))}"

        self.title = f'{self.trigger.head} {self.trigger.perform} {self.FIT_amount} FIT'

        self.squares = int( (self.raw_full_amount / .1 ** -5 ) / 3.33 )
        self.squares = self.squares if self.squares > 0 else 1

        self.message = f"{self.dt} [#{self.eth_block}]"
        # @TODO CG: message += f"\nMarket Cap {mc} ..."
        # @TODO CG: message += f"\nPrice: {quote} .. 24h Vol. {vol}"
        self.message += f"\n{self.trigger.action} {self.full_FIT_amount} FIT\n"  # @TODO CG: ({full_IT_amount_usd})
        self.message += f"{'🟩' * self.squares if self.trigger.which != 'sell' else '🟥' * self.squares}"

    def __str__(self):
        return f"{self.message}\n" \
               f"chain = {'SmartChain'}\n" \
               f"block = {self.eth_block}\n" \
               f"date = {self.dt}\n" \
               f"token = {'FIT'}\n" \
               f"amount = {self.FIT_amount}\n" \
               f"which = {self.trigger.which}\n" \
               f"head = {self.trigger.head}\n" \
               f"agent = {self.trigger.agent}\n" \
               f"action = {self.trigger.action}\n" \
               f"perform = {self.trigger.perform}\n"

    def get_buy_lang(self):
        return self.__buy_lang

    def get_sell_lang(self):
        return self.__sell_lang

    def get_transfer_lang(self):
        return self.__transfer_lang


def notify(sound, address, title, text):
    notification.application_name = title
    notification.title = address
    notification.message = text
    notification.audio = sound
    notification.send()


def change_working_dir():
    os.chdir(__location)


def request_last_tx(url):
    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
    )
    # TODO Get more than just the newest set of last_tx and reverse it!
    return json.loads(r.text)['result'][0]


def get_formatted_time(timestamp):
    dateFormat = "%m/%d/%Y %I:%M%p"
    return datetime.fromtimestamp(timestamp).strftime(dateFormat)


def get_trigger(_from, _to, _lp, lang):
    if _from == _lp:
        return lang['buy']
    elif _to == _lp:
        return lang['sell']
    else:
        return lang['transfer']


def create_database(cursor):
    sql = '''
    CREATE TABLE IF NOT EXISTS tx ( 
        block int UNIQUE NOT NULL,
        chain VARCHAR(255) DEFAULT 'smartchain',
        token_name VARCHAR(20) DEFAULT 'FitScrypt',
        token VARCHAR(20) DEFAULT 'FIT',
        hash VARCHAR(255) DEFAULT '',
        date VARCHAR(255) DEFAULT '',
        time_stamp VARCHAR(255) DEFAULT '',
        wallet_address VARCHAR(255) DEFAULT '',
        amount VARCHAR(20) DEFAULT '',
        full_amount VARCHAR(20) DEFAULT '',
        which VARCHAR(10) DEFAULT '',
        head VARCHAR(255) DEFAULT '',
        agent VARCHAR(255) DEFAULT '',
        action VARCHAR(255) DEFAULT '',
        perform VARCHAR(255) DEFAULT '',
        data TEXT DEFAULT '',
        PRIMARY KEY (block)
    );'''

    cursor.execute(sql)


def write_tx_record(*args):
    sql = f'''INSERT OR REPLACE INTO tx (block, hash, date, time_stamp, wallet_address, amount, full_amount, which, head, agent, action, perform, data)
             VALUES(
                "{args[0]}",
                "{args[1]}",
                "{args[2]}",
                "{args[3]}",
                "{args[4]}",
                "{args[5]}",
                "{args[6]}",
                "{args[7]}",
                "{args[8]}",
                "{args[9]}",
                "{args[10]}",
                "{args[11]}",
                "{args[12]}"
                );'''
    cursor.execute(sql)
    # Commit the changes in the database
    conn.commit()


if __name__ == "__main__":
    try:
        change_working_dir()
        with open('__STARTBLOCK', 'r') as settings:
            start_block = int(settings.readline().replace('\n', ''))
            # if len(sys.argv) > 1:
            #    self.start_block += -abs(int(sys.argv[2]))
            # print(start_block)
    except Exception as e:
        start_block = 14176196

    change_working_dir()
    conn = sqlite3.connect('bscscan_tx.sqlite')
    # Connect to SQLite table
    cursor = conn.cursor()
    create_database(cursor)
    conn.commit()

    FIT = FITToken(int(start_block))

    processed = {}
    for x in reversed(FIT.data):
        tx = Transaction(x, FIT.lp_address)
        argList = [x['blockNumber'],
                   x['hash'],
                   tx.dt,
                   x['timeStamp'],
                   tx.wallet_address,
                   tx.raw_full_amount,
                   tx.full_FIT_amount,
                   tx.trigger.which,
                   tx.trigger.head,
                   tx.trigger.agent,
                   tx.trigger.action,
                   tx.trigger.perform,
                   x]
        if x['blockNumber'] in processed:
            if tx.raw_full_amount > processed[x['blockNumber']]:
                # store entry into SQL database
                write_tx_record(*argList)
        else:
            # block, date, wallet_address, amount, full_amount, head, agent, action, perform, data
            # store entry into SQL database
            write_tx_record(*argList)

    if len(FIT.data) >= 1:
        last_tx = Transaction(FIT.last_tx, FIT.lp_address)

        if last_tx.eth_block >= start_block:
            change_working_dir()
            with open('__STARTBLOCK', 'w') as settings:
                new_start_block = last_tx.eth_block + 1
                settings.write(str(new_start_block))
                print('+', end="")

            if last_tx.trigger.which != 'transfer':
                playsound = './resource/audio/short-confirm.wav' if last_tx.trigger.which == 'buy' else './resource/audio/opt-stop-whining.wav'
                notify(playsound, f"{last_tx.wallet_address[:6]}...{last_tx.wallet_address[-4:]}", last_tx.title, last_tx.message)

    else:
        print('/', end="")

    # Closing the connection
    conn.close()
