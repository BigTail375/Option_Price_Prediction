import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract, ContractDetails
from ibapi.scanner import ScannerSubscription

class SymbolWrapper(EWrapper):
    def __init__(self):
        self.symbols = []
    def scannerData(self, reqId, rank, contractDetails: ContractDetails, distance, benchmark, projection, legsStr):
        self.symbols.append(contractDetails.contract.symbol)
    def scannerDataEnd(self, reqId):
        self.completed = True


class SymbolClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
    def scannerData(self, reqId, rank, contractDetails: ContractDetails, distance, benchmark, projection, legsStr):
        self.wrapper.scannerData(reqId, rank, contractDetails, distance, benchmark, projection, legsStr)
    def scannerDataEnd(self, reqId):
        self.wrapper.scannerDataEnd(reqId)

def get_symbols():
    wrapper = SymbolWrapper()
    client = SymbolClient(wrapper)
    client.connect("127.0.0.1", 7497, clientId=0) 

    scannerSubscription = ScannerSubscription()
    scannerSubscription.instrument = "STK"  
    scannerSubscription.locationCode = "STK.US.MAJOR"  
    scannerSubscription.scanCode = "TOP_PERC_GAIN" 

    client.reqScannerSubscription(1, scannerSubscription, [], [])

    while not hasattr(wrapper, 'completed') or not wrapper.completed:
        client.runOnce()

    client.disconnect()

    return wrapper.symbols

class HistoryWrapper(EWrapper):
    def __init__(self):
        self.data = []
    def historicalData(self, reqId, bar):
        self.data.append(bar)
    def historicalDataEnd(self, reqId, start, end):
        self.df = pd.DataFrame(self.data)


class HistoryClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

    def error(self, reqId, errorCode, errorString):
        print(f"Error: {errorCode} {errorString}")

    def historicalData(self, reqId, bar):
        self.wrapper.historicalData(reqId, bar)

    def historicalDataEnd(self, reqId, start, end):
        self.wrapper.historicalDataEnd(reqId, start, end)

def get_historical_data():
    wrapper = HistoryWrapper()
    client = HistoryClient(wrapper)
    client.connect("127.0.0.1", 7497, clientId=0)

    symbols =  get_symbols()

    for symbol in symbols:
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        client.reqHistoricalData(len(wrapper.data), contract, "", "3 M", "1 day", "TRADES", 0, 1, False, [])

    client.run()
    client.disconnect()

    return wrapper.df

class StockWrapper(EWrapper):
    def __init__(self):
        self.data = []
    def historicalData(self, reqId, bar):
        self.data.append({
            'Symbol': reqId,
            'Date': bar.date,
            'Open': bar.open,
            'High': bar.high,
            'Low': bar.low,
            'Close': bar.close,
            'Volume': bar.volume
        })
    def historicalDataEnd(self, reqId, start, end):
        self.completed = True


class StockClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
    def historicalData(self, reqId, bar):
        self.wrapper.historicalData(reqId, bar)
    def historicalDataEnd(self, reqId, start, end):
        self.wrapper.historicalDataEnd(reqId, start, end)


def get_historical_stock_data():
    wrapper = StockWrapper()
    client = StockClient(wrapper)
    client.connect("127.0.0.1", 7497, clientId=0)

    symbols = get_symbols()

    for i, symbol in enumerate(symbols):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        client.reqHistoricalData(i, contract, "", "3 M", "1 day", "TRADES", 0, 1, False, [])

    while not hasattr(wrapper, 'completed') or not wrapper.completed:
        client.runOnce()
    client.disconnect()
    return pd.DataFrame(wrapper.data)

class OptionWrapper(EWrapper):
    def __init__(self):
        self.data = []

    def historicalData(self, reqId, bar):
        self.data.append({
            'Symbol': reqId,
            'Contract': bar.contract.symbol,
            'Underlying': bar.contract.underlyingSymbol,
            'Expiration': bar.contract.lastTradeDateOrContractMonth,
            'Type': bar.contract.right,
            'Strike': bar.contract.strike,
            'Style': bar.contract.multiplier,
            'Bid': bar.bid,
            'Bid_Size': bar.bidSize,
            'Ask': bar.ask,
            'Ask_Size': bar.askSize,
            'Volume': bar.volume,
            'Open_Interest': bar.openInterest,
            'Quote_Date': bar.date,
            'Delta': bar.delta,
            'Gamma': bar.gamma,
            'Theta': bar.theta,
            'Vega': bar.vega,
            'Implied_Volatility': bar.impliedVolatility
        })
    def historicalDataEnd(self, reqId, start, end):
        self.completed = True


class OptionClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

    def historicalData(self, reqId, bar):
        self.wrapper.historicalData(reqId, bar)

    def historicalDataEnd(self, reqId, start, end):
        self.wrapper.historicalDataEnd(reqId, start, end)


def get_historical_option_data():
    wrapper = OptionWrapper()
    client = OptionClient(wrapper)
    client.connect("127.0.0.1", 7497, clientId=0) 

    symbols = get_symbols()

    for i, symbol in enumerate(symbols):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"

        client.reqHistoricalData(i, contract, "", "3 M", "1 day", "TRADES", 0, 1, False, [])

    while not hasattr(wrapper, 'completed') or not wrapper.completed:
        client.runOnce()

    client.disconnect()

    return pd.DataFrame(wrapper.data)


symbols_list = get_symbols()
print(symbols_list)
