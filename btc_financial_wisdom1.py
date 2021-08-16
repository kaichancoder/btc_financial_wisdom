from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

from financial_wisdom_btc_strategy import TestStrategy

if __name__ == '__main__':

    # Create a cerebro entity
    cerebro = bt.Cerebro(runonce=False)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # or use cheat-on-close
    cerebro.addsizer(bt.sizers.PercentSizer, percents=99)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'BTC_USD_bitfinex_1d_1_Jan_2016_31_July_2021.csv')

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2016, 1, 1),
        todate=datetime.datetime(2021, 7, 31),
        reverse=False,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # resample data for weekly
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks, compression=1)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0)

    # Print out the starting conditions
    # print('Starting Portfolio Value: %,.2f' % locale.format_string('%.2f', cerebro.broker.getvalue(), True))

    # print("{:,d}".format(cerebro.broker.getvalue()))
    num = 10000000
    #locale.setlocale(locale.LC_ALL, '')
    #locale.format_string('%d', 1000000)
    print('Starting Portfolio Value: {:,}'.format(round(cerebro.broker.getvalue(), 0)))

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('\nFinal Portfolio Value: {:,}'.format(round(cerebro.broker.getvalue(), 0)))

    # Plot the result
    cerebro.plot(
        style='line',

        #  Format string for the display of ticks on the x axis
        fmt_x_ticks='%Y-%b-%d %H:%M',

        # Format string for the display of data points values
        fmt_x_data='%Y-%b-%d %H:%M'
    )