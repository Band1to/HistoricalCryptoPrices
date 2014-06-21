import calendar
import datetime
import csv
import os

import arrow
import requests

from django.db import models
from django.conf import settings

class PriceTick(models.Model):
    currency = models.CharField(max_length=8) # btc/ltc/doge/etc.
    exchange = models.CharField(max_length=32)
    base_fiat = models.CharField(max_length=8) # USD/EUR/GBP/etc
    date = models.DateTimeField(db_index=True)
    price = models.FloatField()

    def __unicode__(self):
        return "%s %s %s" % (self.date, self.price, self.exchange)

    @classmethod
    def nearest(self, date):
        """
        Find the tick nearest the passed in date.
        """
        return self.objects.filter(date__lt=date).latest()

    class Meta:
        get_latest_by = 'date'


def load_btc():
    # http://api.bitcoincharts.com/v1/csv/
    f = open(os.path.join(settings.CSV_PATH, "bitstampUSD.csv"))
    for i, line in enumerate(f.readlines()):
        timestamp, price, volume = line.split(",")
        tick_date = datetime.datetime.fromtimestamp(int(timestamp))

        if i % 300 == 0:
            PriceTick.objects.create(
                currency='BTC',
                exchange='bitstampUSD',
                base_fiat='USD',
                date=tick_date,
                price=price,
            )

            print tick_date, price

def load_ltc():
    # http://www.quandl.com/TAMMER1/LTCUSD-Litecoin-LTC-vs-US-Dollar-USD-BTC-e
    with open(os.path.join(settings.CSV_PATH, "TAMMER1-LTCUSD.csv"), 'rb') as f:
        reader = csv.DictReader(f)
        for line in reader:
            tick_date = arrow.get(line['Date']).datetime
            PriceTick.objects.create(
                currency='LTC',
                exchange='btc-e',
                base_fiat='USD',
                date=tick_date,
                price=line['Close'],
            )



def load_doge():
    # http://www.quandl.com/DOGE/USDCRYPTSY-United-States-Dollar-per-Dogecoin-Cryptsy
    with open(os.path.join(settings.CSV_PATH, "DOGE-USDCRYPTSY.csv"), 'rb') as f:
        reader = csv.DictReader(f)
        for line in reader:
            tick_date = arrow.get(line['Date']).datetime
            PriceTick.objects.create(
                currency='DOGE',
                exchange='Crypsy',
                base_fiat='USD',
                date=tick_date,
                price=line['Rate'],
            )


def load_vtc():
    # NOTE: you must run the load_btc function first, as this one depends on it
    # http://www.quandl.com/CRYPTOCHART/VTC-VTC-BITCOIN-Exchange-Rate
    with open(os.path.join(settings.CSV_PATH, "CRYPTOCHART-VTC.csv"), 'rb') as f:
        reader = csv.DictReader(f)
        for line in reader:
            tick_date = arrow.get(line['Date']).datetime
            btc_price = float(line['Price'])
            exchange = PriceTick.nearest(tick_date).price
            PriceTick.objects.create(
                currency='VTC',
                exchange='cryptocoincharts.info',
                base_fiat='USD',
                date=tick_date,
                price=btc_price * exchange,
            )

def load_ppc():
    # NOTE: you must run the load_btc function first, as this one depends on it
    # http://www.quandl.com/CRYPTOCHART/PPC-PPC-BITCOIN-Exchange-Rate
    with open(os.path.join(settings.CSV_PATH, "CRYPTOCHART-PPC.csv"), 'rb') as f:
        reader = csv.DictReader(f)
        for line in reader:
            tick_date = arrow.get(line['Date']).datetime
            btc_price = float(line['Price'])
            exchange = PriceTick.nearest(tick_date).price
            PriceTick.objects.create(
                currency='PPC',
                exchange='cryptocoincharts.info',
                base_fiat='USD',
                date=tick_date,
                price=btc_price * exchange,
            )

def load_all():
    load_btc()
    load_ltc()
    load_doge()
    load_vtc()
    load_ppc()

def get_ticks():
    """
    Run this function every 10 or so minutes so to keep the PriceTicks table
    fresh.
    """
    tick_date = datetime.datetime.now()
    url = "https://www.dogeapi.com/wow/v2/?a=get_current_price&convert_to=USD&amount_doge=1"
    response = requests.get(url)
    price = response.json()['data']['amount']

    PriceTick.objects.create(
        currency='Doge',
        exchange='dogeapi',
        base_fiat='USD',
        date=tick_date,
        price=price,
    )

    ###########################

    tick_date = datetime.datetime.now()
    response = requests.get("https://btc-e.com/api/2/ltc_usd/ticker")
    price = response.json()['ticker']['avg']

    PriceTick.objects.create(
        currency='LTC',
        exchange='btc-e',
        base_fiat='USD',
        date=tick_date,
        price=price,
    )

    ###########################

    tick_date = datetime.datetime.now()
    response = requests.get("https://www.bitstamp.net/api/ticker/")
    price = response.json()['last']

    PriceTick.objects.create(
        currency='BTC',
        exchange='bitstampUSD',
        base_fiat='USD',
        date=tick_date,
        price=price,
    )

    ###########################
