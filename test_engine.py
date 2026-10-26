from decimal import Decimal as D
import unittest
from arb_engine import Quote, SymbolRules, PaperArbitrageEngine

NOW=1_800_000_000_000

def q(symbol, base, quote, bid, bidq, ask, askq, t=NOW):
    return Quote(symbol, base, quote, D(str(bid)), D(str(bidq)), D(str(ask)), D(str(askq)), t)

def r(symbol, base, quote, step='0.000001', minq='0.000001', minn='0'):
    return SymbolRules(symbol, base, quote, D(step), D(minq), D(minn))

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.e = PaperArbitrageEngine(fee_rate=D('0.001'), slippage_rate=D('0.0002'), max_quote_age_ms=1000, max_snapshot_skew_ms=250)

    def test_profitable_cycle_after_costs(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,100),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),
            q('ETHUSDT','ETH','USDT',5.2,1000,5.21,1000),
        )
        rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        res=self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertTrue(res.executable)
        self.assertGreater(res.net_pnl,D('0'))

    def test_unprofitable_cycle(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,100),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),
            q('ETHUSDT','ETH','USDT',4.95,1000,4.96,1000),
        )
        rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        res=self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertTrue(res.executable)
        self.assertLess(res.net_pnl,D('0'))

    def test_stale_quote_rejected(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,100,NOW-5000),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),
            q('ETHUSDT','ETH','USDT',5.2,1000,5.21,1000),
        )
        rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        res=self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertFalse(res.executable)
        self.assertEqual(res.reject_reason,'stale_quote')

    def test_snapshot_skew_rejected(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,100,NOW-300),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000,NOW),
            q('ETHUSDT','ETH','USDT',5.2,1000,5.21,1000,NOW),
        )
        rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        res=self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertFalse(res.executable)
        self.assertEqual(res.reject_reason,'snapshot_skew')

    def test_insufficient_depth_rejected(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,0.1),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),
            q('ETHUSDT','ETH','USDT',5.2,1000,5.21,1000),
        )
        rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        res=self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertFalse(res.executable)
        self.assertEqual(res.reject_reason,'insufficient_top_depth')

    def test_min_notional_rejected(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,100),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),
            q('ETHUSDT','ETH','USDT',5.2,1000,5.21,1000),
        )
        rules=(r('BTCUSDT','BTC','USDT',minn='100'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        res=self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertFalse(res.executable)
        self.assertEqual(res.reject_reason,'min_notional')

    def test_fee_changes_profitability(self):
        quotes=(
            q('BTCUSDT','BTC','USDT',99.9,100,100,100),
            q('ETHBTC','ETH','BTC',0.0499,1000,0.05,1000),
            q('ETHUSDT','ETH','USDT',5.03,1000,5.04,1000),
        )
        rules=(r('BTCUSDT','BTC','USDT'),r('ETHBTC','ETH','BTC'),r('ETHUSDT','ETH','USDT'))
        zero = PaperArbitrageEngine(D('0'),D('0'),1000,250).evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        cost = self.e.evaluate_cycle(D('68'),('USDT','BTC','ETH','USDT'),quotes,rules,NOW)
        self.assertGreater(zero.net_pnl, cost.net_pnl)

if __name__ == '__main__':
    unittest.main(verbosity=2)
