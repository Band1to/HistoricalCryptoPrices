import calendar
import datetime
import csv
import os
import StringIO

import arrow
import requests
import pytz

from django.db import models
from django.conf import settings

from pycryptoprices import CryptoPriceGetter

class PriceTick(models.Model):
    currency = models.CharField(max_length=8) # btc/ltc/doge/etc.
    exchange = models.CharField(max_length=128) # kraken/bitstamp/etc.
    base_fiat = models.CharField(max_length=8) # USD/EUR/GBP/etc.
    date = models.DateTimeField(db_index=True)
    price = models.FloatField()

    def __unicode__(self):
        return "%s %s %s->%s" % (self.date, self.price, self.currency, self.base_fiat)

    @classmethod
    def nearest(self, date):
        """
        Find the tick nearest the passed in date.
        """
        return self.objects.filter(date__lt=date).latest()

    class Meta:
        get_latest_by = 'date'


def load_btc():
    # $ cd ~
    # $ wget http://api.bitcoincharts.com/v1/csv/bitstampUSD.csv.gz | unp
    from os.path import expanduser
    home = os.path.expanduser("~")
    f = open(os.path.join(home, "bitstampUSD.csv"))
    for i, line in enumerate(f):
        timestamp, price, volume = line.split(",")
        tick_date = datetime.datetime.fromtimestamp(int(timestamp)).replace(tzinfo=pytz.UTC)

        if i % 300 == 0:
            p = PriceTick.objects.create(
                currency='BTC',
                exchange='bitstampUSD',
                base_fiat='USD',
                date=tick_date,
                price=price,
            )

            print p

def load_ltc():
    # http://www.quandl.com/TAMMER1/LTCUSD-Litecoin-LTC-vs-US-Dollar-USD-BTC-e
    url = "http://www.quandl.com/api/v1/datasets/TAMMER1/LTCUSD.csv"
    response = requests.get(url)
    reader = csv.DictReader(StringIO.StringIO(response.content))
    for line in reader:
        tick_date = arrow.get(line['Date']).datetime
        p = PriceTick.objects.create(
            currency='LTC',
            exchange='btc-e',
            base_fiat='USD',
            date=tick_date,
            price=line['Close'],
        )
        print p



def load_doge():
    # http://www.quandl.com/DOGE/USDCRYPTSY-United-States-Dollar-per-Dogecoin-Cryptsy
    url = "http://www.quandl.com/api/v1/datasets/DOGE/USDCRYPTSY.csv"
    response = requests.get(url)
    reader = csv.DictReader(StringIO.StringIO(response.content))
    for line in reader:
        tick_date = arrow.get(line['Date']).datetime
        p = PriceTick.objects.create(
            currency='DOGE',
            exchange='DOGE/USDCRYPTSY',
            base_fiat='USD',
            date=tick_date,
            price=line['Rate'],
        )
        print p


def load_vtc():
    # NOTE: you must run the load_btc function first, as this one depends on it
    # http://www.quandl.com/CRYPTOCHART/VTC-VTC-BITCOIN-Exchange-Rate
    url = "http://www.quandl.com/api/v1/datasets/CRYPTOCHART/VTC.csv"
    response = requests.get(url)
    reader = csv.DictReader(StringIO.StringIO(response.content))
    for line in reader:
        tick_date = arrow.get(line['Date']).datetime
        btc_price = float(line['Price'])
        exchange = PriceTick.nearest(tick_date).price
        p = PriceTick.objects.create(
            currency='VTC',
            exchange='cryptocoincharts.info',
            base_fiat='USD',
            date=tick_date,
            price=btc_price * exchange,
        )
        print p


def load_ppc():
    # NOTE: you must run the load_btc function first, as this one depends on it
    # http://www.quandl.com/CRYPTOCHART/PPC-PPC-BITCOIN-Exchange-Rate
    url = "http://www.quandl.com/api/v1/datasets/CRYPTOCHART/PPC.csv"
    response = requests.get(url)
    reader = csv.DictReader(StringIO.StringIO(response.content))
    for line in reader:
        tick_date = arrow.get(line['Date']).datetime
        btc_price = float(line['Price'])
        exchange = PriceTick.nearest(tick_date).price
        p = PriceTick.objects.create(
            currency='PPC',
            exchange='cryptocoincharts.info',
            base_fiat='USD',
            date=tick_date,
            price=btc_price * exchange,
        )
        print p


def load_nxt():
    url = "http://www.quandl.com/api/v1/datasets/CRYPTOCHART/NXT.csv"
    response = requests.get(url)
    reader = csv.DictReader(StringIO.StringIO(response.content))
    for line in reader:
        tick_date = arrow.get(line['Date']).datetime
        btc_price = float(line['Price'])
        exchange = PriceTick.nearest(tick_date).price
        p = PriceTick.objects.create(
            currency='NXT',
            exchange='cryptocoincharts.info (via quandl.com)',
            base_fiat='USD',
            date=tick_date,
            price=btc_price * exchange,
        )
        print p

def load_ftc():
    url = "http://www.quandl.com/api/v1/datasets/CRYPTOCHART/FTC.csv"
    response = requests.get(url)
    reader = csv.DictReader(StringIO.StringIO(response.content))
    for line in reader:
        tick_date = arrow.get(line['Date']).datetime
        btc_price = float(line['Price'])
        exchange = PriceTick.nearest(tick_date).price
        p = PriceTick.objects.create(
            currency='FTC',
            exchange='cryptocoincharts.info (via quandl.com)',
            base_fiat='USD',
            date=tick_date,
            price=btc_price * exchange,
        )
        print p

def load_all():
    load_btc()
    load_ltc()
    load_doge()
    load_vtc()
    load_ppc()
    load_nxt()
    load_ftc()

def get_ticks():
    """
    Run this function every 10 or so minutes so to keep the PriceTicks table
    fresh.
    """
    getter = CryptoPriceGetter(useragent='HistoricalCryptoPrice.pricetick.models.get_ticks')
    all_ticks = []
    for fiat in ['usd', 'cad', 'btc', 'rur', 'eur']:
        for crypto in ['btc', 'ltc', 'doge', 'nxt', 'ppc', 'vtc', 'ftc']:
            price, market = getter.get_price(fiat, crypto)
            all_ticks.append(
                PriceTick.objects.create(
                    currency=crypto.upper(),
                    exchange=market,
                    base_fiat=fiat.upper(),
                    date=datetime.datetime.now(),
                    price=price,
                )
            )

    return all_ticks
