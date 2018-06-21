#----------------------------------------------------------------------------------------------------------
import bs4 as bs 
import datetime as dt 
import matplotlib.pyplot as plt 
from matplotlib import style 
import os 
import pandas as pd 
import pandas_datareader as web
from pandas_datareader._utils import RemoteDataError 
import pickle 
import requests 
import numpy as np 
#----------------------------------------------------------------------------------------------------------
def save_nifty50_tickers():
	resp = requests.get('https://en.wikipedia.org/wiki/NIFTY_50')
	soup = bs.BeautifulSoup(resp.text, "lxml")
	table = soup.find('table', {'class' : 'wikitable sortable'})
	tickers = []

	for row in table.findAll('tr')[1:]:
		ticker = row.findAll('td')[1].text 
		tickers.append(ticker+'.NS')

	with open("nifty50tickers.pickle", "wb") as f:
		pickle.dump(tickers, f)

	print(tickers)
	return tickers 
#----------------------------------------------------------------------------------------------------------
def get_data_from_yahoo(reload_nifty50 = False):

	if reload_nifty50:
		tickers = save_nifty50_tickers()
	else:
		with open("nifty50tickers.pickle", "rb") as f:
			tickers = pickle.load(f)

	if not os.path.exists('Data/Nifty50_stock_dfs'):
		os.makedirs('Data/Nifty50_stock_dfs')

	start = dt.datetime(2000, 1, 1)
	end = dt.datetime(2018, 1, 31)

	for ticker in tickers:
		print(ticker)
		if not os.path.exists('Data/Nifty50_stock_dfs/{}.csv'.format(ticker)):
			try:
				df = web.DataReader(ticker, 'yahoo', start, end)
				df.to_csv('Data/Nifty50_stock_dfs/{}.csv'.format(ticker))
			except RemoteDataError:
				# Handle error
				#print("No information for {}.".format(ticker))
				#ticker_dict = {'HPCL.NS' : 'HINDPETRO.NS', 'ITC.NS' : 'ITC.NS', 'TATAMOTORS.NS' : 'TATAMOTORS.NS'}
				#df = web.DataReader(ticker_dict[ticker], 'yahoo', start, end)
				#df.to_csv('Data/Nifty50_stock_dfs/{}.csv'.format(ticker))
				continue
		else:
			print('Already have {}'.format(ticker))
#----------------------------------------------------------------------------------------------------------
def compile_data():
	with open("nifty50tickers.pickle", "rb") as f:
		tickers = pickle.load(f)

		main_df = pd.DataFrame()

		for count, ticker in enumerate(tickers):
			df = pd.read_csv('Data/Nifty50_stock_dfs/{}.csv'.format(ticker))
			df.set_index('Date', inplace = True)

			df.rename(columns = {'Adj Close' : ticker}, inplace = True)
			df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace = True)

			if main_df.empty:
				main_df = df 
			else:
				main_df = main_df.join(df, how = 'outer')

			if count % 10 == 0:
				print("Count : ", count)

		main_df.to_csv('Data/nifty50_joined_closes.csv')
#----------------------------------------------------------------------------------------------------------
#def visualize_data():

#	df = pd.read_csv('sp500_joined_closes.csv')
#	#df['AYI'].plot()
#	#plt.show()
#	df_corr = df.corr()
#
#	print(df_corr.head())
#
#	data = df_corr.values
#	fig = plt.figure()
#	ax = fig.add_subplot(1,1,1)
#
#	heatmap = ax.pcolor(data, cmap = plt.cm.RdYlGn)
#	fig.colorbar(heatmap)
#	ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor =False)
#	ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor =False)
#	ax.invert_yaxis()
#	ax.xaxis.tick_top()
#
#	column_lables = df_corr.columns
#	row_lables = df_corr.index
#
#	ax.set_xticklabels(column_lables)
#	ax.set_yticklabels(row_lables)
#
#	plt.xticks(rotation = 90)
#	heatmap.set_clim(-1, 1)
#	plt.tight_layout()
#	plt.show()
#
#
#visualize_data()
##----------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	#get_data_from_yahoo()
	compile_data()
##----------------------------------------------------------------------------------------------------------