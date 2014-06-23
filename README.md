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
