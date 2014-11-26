HistoricalCryptoPrices
======================
Get the price of a cryptocurrency at a point in time in history. Useful in determining how much USD a bitcoin
transaction was worth at time of transaction.

Installation
============

Clone the repo. This project uses the django web framework, so configure the database according to the django docs.
By default it uses sqlite3. Next run the command `./manage.py preload_prices`
This function downloads historical price data from quandl.com and puts them in to the database.
Next install a cron task to keep the database updated. The command to fetch new prices is `./manage.py fetch_prices`

Currencies supported
====================
* Bitcoin
* Litecoin
* Dogecoin
* Vertcoin
* Peercoin
* NXT
* Feathercoin

Usage
=====

The primary way to use this software is through a RESTful interface.
All endpoints (currently only one), *always* returns valid JSON.

There is an installation of this software running on http://crypto-prices.pw.
It is free for public use, but please be mindful of how much load your application puts on the server.

price_for_date
--------------


| argument   | description                                                           |
-------------|------------------------------------------------------------------------
| date       | Either unix timestamp or ISO 8601, or any format that [arrow.get](http://crsmithdev.com/arrow/#arrow.factory.ArrowFactory.get) takes. *Required* |
| fiat       | Three letter currency code, e.g. usd, cad, btc, rur, eur. *Required*              |
| crypto     | Three letter currency code, e.g. btc, ltc, ppc, vtc, doge, drk. *Required*        |


Response is a two item list. The first item is the price (expressed as a Number),
the second is the source for the number.

e.g:

```
[587.99, "bitstampUSD"]
```

example invocation: http://crypto-prices.pw/price_for_date?fiat=usd&crypto=btc&date=2014-06-24T11:48:16.929922

Coming Soon
===========

* Integration with pycryptoprices library for more robust price recording even if a single API gets changed.
* More currencies.

Donations
=========

If you would like to send a donation to support development, please send BTC here: 1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X
