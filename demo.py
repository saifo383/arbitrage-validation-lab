from decimal import Decimal as D
from arb_engine import Quote, SymbolRules, PaperArbitrageEngine

NOW=1_800_000_000_000
q=lambda s,b,q,bp,bq,ap,aq: Quote(s,b,q,D(str(bp)),D(str(bq)),D(str(ap)),D(str(aq)),NOW)
r=lambda s,b,q: SymbolRules(s,b,q,D('0.000001'),D('0.000001'),D('0'))
eng=PaperArbitrageEngine(D('0.001'),D('0.0002'),1000,250)
quotes=(q('BTCUSDT','BTC','USDT',99.9,100,100,100),q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),q('ETHUSDT','ETH','USDT',5.2,1000,5.21,1000))
rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
res=eng.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
print('synthetic executable:',res.executable)
print('start:',res.start_amount)
print('end:',res.end_amount)
print('gross_return_pct:',res.gross_return_pct.quantize(D('0.0001')))
print('net_return_pct:',res.net_return_pct.quantize(D('0.0001')))
print('net_pnl:',res.net_pnl.quantize(D('0.000001')))
