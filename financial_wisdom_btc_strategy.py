# Import the backtrader platform
import backtrader as bt


class TestStrategy(bt.Strategy):

    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s %s' % (dt.isoformat(), txt), end='')
        print('%s %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] data series
        self.dataclose = self.datas[0].close
        self.first = None
        self.last = None
        self.val_start = None

        # To keep track of pending orders
        self.order = None
        # self.buyprice = None
        # self.buycomm = None
        self.dailySL = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod
        )

        # MACD indicator used
        self.macd = bt.indicators.MACD(self.data0)
        self.macdWeek = bt.indicators.MACD(self.data1)

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.mcrossWeek = bt.indicators.CrossOver(self.macdWeek.macd, self.macdWeek.signal)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order is submitted or accepted, nothing to do
            return

        # Check if an order has been completed
        # Broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                print('BUY EXECUTED, %s Price: %.2f, Size: %.2f BTC, Cost: %.2f, Comm: %.2f, Port Val: %.2f' %
                      (self.datas[0].datetime.date(0).isoformat(),
                       order.executed.price,
                       order.executed.size,
                       order.executed.value,
                       order.executed.comm,
                       self.broker.getvalue()))

                if self.first is None:
                    self.first = order.executed.price

            elif order.issell():
                print('SELL EXECUTED, %s Price: %.2f, Original Price: %.2f, Comm: %.2f' %
                      (self.datas[0].datetime.date(0).isoformat(),
                       order.executed.price,
                       order.executed.value,
                       order.executed.comm
                       ))

                self.last = order.executed.price

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order is Cancelled or Margin or Rejected, %s' % str(order.status))

        # No pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

        print('-------------------------------------------------\n')

    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def stop(self):
        print('BnH Start: ', self.val_start)

        buy_hold = (self.val_start/self.first)*self.last
        print('BnH End: {:,}'.format(round(buy_hold, 0)))

    def next(self):
        # Simply log the closing price of the series from the reference
        # sys.stdout.write(".")
        # print(".", end='')

        # Check if an order is pending ... if yes, w cannot do a 2nd order
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Buy
            # We first make sure macd weekly is positive, and also daily is positive
            # Doesn't matter if macd line is below zero, we don't care it has crossed signal
            if (    (self.mcross[0] > 0.0) and
                    (self.macdWeek.macd[0] > self.macdWeek.signal[0])):

            #if (    (self.mcross[0] > 0.0) and
            #        (self.macdWeek.macd[0] > self.macdWeek.signal[0]) and
            #        (self.macdWeek.macd[-1] > self.macdWeek.macd[-2]) and
            #        (self.macdWeek.macd[-2] > self.macdWeek.macd[-3])
            #        ):
                self.order = self.buy()

                # reset
                self.dailySL = None

        else:

            # if daily macd is below 0, we take the lowest point
            if (self.mcross[0] < 0.0):
                self.dailySL = self.data.low[0]
                #self.log('SL, %s' % str(self.dailySL))

            if (self.mcross[0] > 0.0):
                self.dailySL = None
                #self.log('Reset')

            # Sell
            if self.dailySL is not None:
                if (    (self.dataclose[0] < self.dailySL) or
                        (self.mcrossWeek[0] < 0.0)):
                    # SELL!
                    # self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.sell()