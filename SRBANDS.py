import numpy as np
import pandas as pd


# Create the class
class SRBANDS():

    # Initialize the class
    def __init__(self, symbol, periods , intervals):
        self.df = self._extract_data(symbol, periods, intervals)
        


    # Extract data
    def _extract_data(self, symbol, periods, intervals):
        # import yfinance as yf
        # data = yf.download(tickers=symbol, period=periods , interval=intervals)
        data = pd.read_csv('./XAUUSD_H1_201807110100_202307112100.csv', sep='\t')
        data['Datetime'] = pd.to_datetime(data['<DATE>'] + " " + data['<TIME>'])
        data = data.set_index('Datetime')
        data = data.drop(['<DATE>','<TIME>'], axis=1)
        data = data.drop(['<OPEN>','<TICKVOL>' ,'<VOL>','<SPREAD>'] , axis=1)
        data = self._calculate_return(data)
        data = self._ichimuko_indicator(data)
        data = self._srbands_indicator(data)
        data['SIGNAL'] = 0
        data.loc[data["RETURN"] >  1.0, "SIGNAL"] =  1
        data.loc[data["RETURN"] < -1.0, "SIGNAL"] =  2
        data = data.drop(['RETURN'] , axis=1)
        data.rename(columns = {'<CLOSE>':'CLOSE'}, inplace = True)
        data.rename(columns = {'<HIGH>':'HIGH'}, inplace = True)
        data.rename(columns = {'<LOW>':'LOW'}, inplace = True)
        data.dropna(inplace=True)

        return data


    # Calculates general period returns and volatility
    def _calculate_return(self, df):
        df["RETURN"] = df['<CLOSE>'].shift(-1) - df["<CLOSE>"]
        
        df.dropna(inplace=True)
        return df
    
    # calculate Ichimuko Indicator
    def _ichimuko_indicator(self,df):
        # Tenkan-sen 
        nine_high = df['<HIGH>'].rolling(window=9).max()
        nine_low = df['<LOW>'].rolling(window=9).min()
        df["TS"] = (nine_high + nine_low) / 2
        
        # Kijun-sen 
        twenty_six_high = df['<HIGH>'].rolling(window=26).max()
        twenty_six_low = df['<LOW>'].rolling(window=26).min()
        df["KS"] = (twenty_six_high + twenty_six_low) / 2
        
        # Senkou Span A 
        df["SSA"] = (df["TS"].shift(26) + df["KS"].shift(26)) / 2
        
        # Senkou Span B 
        fifty_two_high = df['<HIGH>'].shift(26).rolling(window=52).max() 
        fifty_two_low = df['<LOW>'].shift(26).rolling(window=52).min()
        df["SSB"] = (fifty_two_high + fifty_two_low) / 2
        
        # The most current closing price plotted 26 periods behind 
        # df["CS"] = df['<CLOSE>'].shift(-26)

        #return the dataset
        return df
    
    def _srbands_indicator(self,df):
        # Calculate the upper band
        SSA = (df["TS"] + df["KS"]) / 2
        upper = SSA.rolling(window=52).max()
        
        # Calculate the middle band
        fifty_two_high = df['<HIGH>'].rolling(window=52).max() 
        fifty_two_low = df['<LOW>'].rolling(window=52).min()
        middle = (fifty_two_high + fifty_two_low) / 2
        
        # Calculate the lower band
        lower = SSA.rolling(window=52).min()
        
        # Add bands to the dataframe
        df["UB"] = upper
        df["MB"] = middle
        df["LB"] = lower
        
        # Return the dataframe
        return df