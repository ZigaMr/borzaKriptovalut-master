import matplotlib.pyplot as plt
import requests
import pandas as pd
import json

data = requests.get(r'https://www.bitstamp.net/api/v2/order_book/ethbtc')
data = data.json()

bids = pd.DataFrame()
bids['quantity'] = [i[1] for i in data['bids']]
bids['price'] = [i[0] for i in data['bids']]
asks = pd.DataFrame()
asks['price'] = [i[0] for i in data['asks']]
asks['quantity'] = [i[1] for i in data['asks']]

asks.price = asks.price.apply(float)
asks.quantity = asks.quantity.apply(float)

bids.price = bids.price.apply(float)
bids.quantity = bids.quantity.apply(float)

bids_dict = {x[1]:x[0] for x in bids.itertuples(index=False)}
asks_dict = {x[0]:x[1] for x in asks.itertuples(index=False)}
bidask = dict()
bidask['asks'] = asks_dict
bidask['bids'] = bids_dict

data['asks'] = [{'price':float(i[0]), 'amount':float(i[1])} for i in data['asks']]
data['bids'] = [{'price':float(i[0]), 'amount':float(i[1])} for i in data['bids']]
with open('order_book2.json', 'w') as fp:
    json.dump(data, fp)

def plot_ob(bidask, bps=.25):
    # bps: basis points

    best_bid = max(bidask["bids"].keys())
    best_ask = min(bidask["asks"].keys())
    worst_bid = best_bid * (1 - bps)
    worst_ask = best_bid * (1 + bps)
    filtered_bids = sorted(filter(lambda k: k[0] >= worst_bid, bidask['bids'].items()), key=lambda x:-x[0])
    filtered_asks = sorted(filter(lambda k: k[0] <= worst_ask, bidask['asks'].items()), key=lambda x:+x[0])

    bsizeacc = 0
    bhys = []    # bid - horizontal - ys
    bhxmins = [] # bid - horizontal - xmins
    bhxmaxs = [] # ...
    bvxs = []
    bvymins = []
    bvymaxs = []
    asizeacc = 0
    ahys = []
    ahxmins = []
    ahxmaxs = []
    avxs = []
    avymins = []
    avymaxs = []
    
    for (p1, s1), (p2, s2) in zip(filtered_bids, filtered_bids[1:]):
        bvymins.append(bsizeacc)
        if bsizeacc == 0:
            bsizeacc += s1
        bhys.append(bsizeacc)
        bhxmins.append(p2)
        bhxmaxs.append(p1)
        bvxs.append(p2)
        bsizeacc += s2
        bvymaxs.append(bsizeacc)
    
    for (p1, s1), (p2, s2) in zip(filtered_asks, filtered_asks[1:]):
        avymins.append(asizeacc)
        if asizeacc == 0:
            asizeacc += s1
        ahys.append(asizeacc)
        ahxmins.append(p1)
        ahxmaxs.append(p2)
        avxs.append(p2)
        asizeacc += s2
        avymaxs.append(asizeacc)
        
    plt.hlines(bhys, bhxmins, bhxmaxs, color="green")
    plt.vlines(bvxs, bvymins, bvymaxs, color="green")
    plt.hlines(ahys, ahxmins, ahxmaxs, color="red")
    plt.vlines(avxs, avymins, avymaxs, color="red")
    
# d_ts = max(ob.keys())
# d_ob = ob[d_ts]
plt.figure(figsize=(5,4))
plot_ob(bidask, bps=.05)
plt.ylim([0, 4000])
plt.show()