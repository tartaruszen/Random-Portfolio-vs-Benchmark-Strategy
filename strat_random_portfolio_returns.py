import sys
import csv
import urllib2
import datetime
import numpy as np
from time import sleep
from random import randint
import matplotlib.pyplot as plt

class RandomPortfolioReturnStrategy(object):

	def __init__(self, lim, bmark_ticker, constituents, n_rand_port):
		self.lim = lim
		self.bmark_ticker = bmark_ticker
		self.constituents = constituents
		self.n_rand_port = n_rand_port
		self.stocklist = self.load_stocklist()
		self.f_portfolios = 'rand_portfolios.csv'

	def load_stocklist(self):
		with open('data/lse_main_stocklist.csv', 'rb') as f_stocklist:
			reader = csv.reader(f_stocklist)
			stocklist = list(reader)
		return stocklist

	def get_rand_stock(self):
		rand_index = rand_index = randint(0, (len(self.stocklist)-1))
		return self.stocklist[rand_index]

	def fetch_prices(self, ticker):
		priceApi = 'http://ichart.finance.yahoo.com/table.csv?s='
		params = '&a=00&b=01&c=2012'
		try:
			data = urllib2.urlopen(priceApi + ticker + params).read()
			data = data.replace('\r', '').split('\n')[1:][::-1]
		except:
			return self.fetch_prices(self.get_rand_stock()[0])
		if len(data) < self.lim:
			return self.fetch_prices(self.get_rand_stock()[0])
		prices = []
		for d in data:
			if d:
				prices.append(float(d.split(',')[6]))
		prices_pct = self.convert_pct(prices)
		return prices_pct

	def convert_pct(self, prices):
		prices_pct = []
		i = 0
		while len(prices_pct) < (len(prices) - 1):
			chng_pc = ((prices[i + 1] / prices[0]) - 1) * 100
			prices_pct.append(chng_pc)
			i += 1
		return prices_pct

	def calculate_portfolio_performance(self, portfolio_prices):
		i = 0
		portfolio_return = []
		while i < self.lim:
			j = 0
			sigma = 0
			while j < len(portfolio_prices):
				sigma += float(portfolio_prices[j][i])
				j += 1
			avg_pc = sigma / j
			portfolio_return.append(avg_pc)
			i += 1
		return portfolio_return

	def plot_results(self, benchmark, rand_portfolios):
		print "\n>> Plotting results..."
		fig = plt.figure()
		fig.canvas.set_window_title('Performance of Benchmark vs Random Portfolio')
		plt.ylabel('% change')
		plt.xlabel('Days')
		plt.plot(benchmark)

		for portfolio in rand_portfolios:
			plt.plot(portfolio)
		
		legend = ['Benchmark (' + self.bmark_ticker + ')']
		for i in xrange(len(rand_portfolios)):
			legend.append('Rand Portfolio (' + str(i+1) + ')')

		plt.legend(legend, loc='upper left', prop={'size':'10'})
		plt.show()

	def run_simulation(self):
		print "\n>> Running simulation calculations..."
		benchmark = self.fetch_prices(self.bmark_ticker)[:self.lim]
		rand_portfolios = []
		done_total = self.n_rand_port * self.constituents

		portfolio_stock_names = np.empty([(self.constituents+1), self.n_rand_port], dtype='S24')
		for n in xrange(self.n_rand_port):
			portfolio = []
			for i in xrange(self.constituents):
				rand_stock = self.get_rand_stock()
				portfolio.append(rand_stock)

			portfolio_prices = []
			portfolio_stock_names[0][n] = 'Rand Portfolio (' + str(n+1) + ')'
			for i, stock in enumerate(portfolio):
				price = self.fetch_prices(stock[0])
				portfolio_prices.append(price)
				portfolio_stock_names[(i+1)][n] = stock[0]

				done_curr = (n * self.constituents) + (i + 1)
				completed = (float(done_curr)/float(done_total)) * 100
				sys.stdout.write("\r%.2f" % completed + "% completed...")
				sys.stdout.flush()

			portfolio_performance = self.calculate_portfolio_performance(portfolio_prices)
			rand_portfolios.append(portfolio_performance)

		print "\n\n>> Finished simulating random portfolios!"
		np.savetxt(self.f_portfolios, portfolio_stock_names, delimiter=',', fmt='%s')
		print ">> Random portfolios constituents saved in:\n", self.f_portfolios
		self.plot_results(benchmark, rand_portfolios)

if __name__ == '__main__':
	historic_days_limit = 360
	benchmark_ticker = '^FTSE'
	benchmark_constituents = 100
	no_of_rand_portfolios = 20

	print "\n*** Random Portfolio vs Benchmark Returns Strategy ***\n"
	print ">> Starting with following paramaters:"
	print "Historical days:\t\t", historic_days_limit
	print "Benchmark ticker:\t\t", benchmark_ticker
	print "Constituent count:\t\t", benchmark_constituents
	print "No. of portfolios to generate:\t", no_of_rand_portfolios

	strat = RandomPortfolioReturnStrategy(historic_days_limit, benchmark_ticker, benchmark_constituents, no_of_rand_portfolios)
	strat.run_simulation()
	print "\n*** Simulation Finished ***"