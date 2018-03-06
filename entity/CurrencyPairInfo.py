class TowEdgesInfo:
    def __init__(self,currency,eth_bids,eth_asks,btc_bids,btc_asks):
        self.currency=currency
        #eth sold
        self.eth_bids=eth_bids
        # eth buy
        self.eth_asks = eth_asks
        #btc sold
        self.btc_bids = btc_bids
        #btc buy
        self.btc_asks = btc_asks
