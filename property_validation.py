from decimal import Decimal as D
from random import Random
from arb_engine import Quote, SymbolRules, PaperArbitrageEngine

rng=Random(20261025)
NOW=1_800_000_000_000
eng=PaperArbitrageEngine(D('0.001'),D('0.0002'),1000,250)

def rules(s,b,q): return SymbolRules(s,b,q,D('0.00000001'),D('0.00000001'),D('0'))
R=(rules('BTCUSDT','BTC','USDT'),rules('ETHBTC','ETH','BTC'),rules('ETHUSDT','ETH','USDT'))

def mk(mid_btc, mid_cross, dislocation=D('0')):
    hs=D('0.0002')
    eth_mid=mid_btc*mid_cross*(D('1')+dislocation)
    return (
        Quote('BTCUSDT','BTC','USDT',mid_btc*(1-hs),D('100'),mid_btc*(1+hs),D('100'),NOW),
        Quote('ETHBTC','ETH','BTC',mid_cross*(1-hs),D('1000'),mid_cross*(1+hs),D('1000'),NOW),
        Quote('ETHUSDT','ETH','USDT',eth_mid*(1-hs),D('1000'),eth_mid*(1+hs),D('1000'),NOW),
    )

false_positive=0
max_net=D('-999')
for _ in range(10000):
    mid_btc=D(str(rng.uniform(10000,150000)))
    mid_cross=D(str(rng.uniform(0.005,0.2)))
    res=eng.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),mk(mid_btc,mid_cross),R,NOW)
    if res.executable and res.net_pnl>0: false_positive += 1
    if res.executable and res.net_return_pct>max_net: max_net=res.net_return_pct

if false_positive != 0:
    raise SystemExit(f'False profitable cases detected: {false_positive}')

print('consistent_market_cases=10000')
print('false_positive_profitable_cases=',false_positive)
print('max_net_return_pct_consistent=',max_net)
print('controlled_dislocation_results:')
for bp in [20,30,40,50,75,100]:
    dis=D(bp)/D('10000')
    res=eng.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),mk(D('50000'),D('0.05'),dis),R,NOW)
    print(bp,'bps gross-mid dislocation -> net_return_pct=',res.net_return_pct,'net_pnl=',res.net_pnl)
