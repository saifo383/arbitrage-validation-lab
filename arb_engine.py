from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from typing import List, Tuple, Optional
import time

getcontext().prec = 28
D = Decimal

@dataclass(frozen=True)
class Quote:
    symbol: str
    base: str
    quote: str
    bid: Decimal
    bid_qty: Decimal
    ask: Decimal
    ask_qty: Decimal
    recv_ms: int

@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    base: str
    quote: str
    step_size: Decimal = D('0.00000001')
    min_qty: Decimal = D('0')
    min_notional: Decimal = D('0')

@dataclass
class LegResult:
    symbol: str
    from_asset: str
    to_asset: str
    side: str
    input_amount: Decimal
    output_before_fee: Decimal
    fee_paid_output_asset: Decimal
    output_after_fee: Decimal
    effective_price: Decimal
    ok: bool
    reject_reason: Optional[str] = None

@dataclass
class CycleResult:
    path: Tuple[str, str, str, str]
    legs: List[LegResult]
    start_amount: Decimal
    end_amount: Decimal
    gross_return_pct: Decimal
    net_return_pct: Decimal
    net_pnl: Decimal
    executable: bool
    reject_reason: Optional[str] = None


def floor_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step

class PaperArbitrageEngine:
    def __init__(self, fee_rate: Decimal = D('0.001'), slippage_rate: Decimal = D('0.0002'), max_quote_age_ms: int = 1000, max_snapshot_skew_ms: int = 250):
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate
        self.max_quote_age_ms = max_quote_age_ms
        self.max_snapshot_skew_ms = max_snapshot_skew_ms

    def _fresh(self, quotes: List[Quote], now_ms: int) -> Optional[str]:
        ages = [now_ms - q.recv_ms for q in quotes]
        if any(a < 0 for a in ages):
            return 'future_timestamp'
        if any(a > self.max_quote_age_ms for a in ages):
            return 'stale_quote'
        times = [q.recv_ms for q in quotes]
        if max(times) - min(times) > self.max_snapshot_skew_ms:
            return 'snapshot_skew'
        return None

    def execute_leg(self, amount: Decimal, from_asset: str, to_asset: str, q: Quote, rules: SymbolRules) -> LegResult:
        if from_asset == q.base and to_asset == q.quote:
            side = 'SELL'
            base_qty = floor_step(amount, rules.step_size)
            if base_qty < rules.min_qty:
                return LegResult(q.symbol, from_asset, to_asset, side, amount, D('0'), D('0'), D('0'), q.bid, False, 'min_qty')
            if base_qty > q.bid_qty:
                return LegResult(q.symbol, from_asset, to_asset, side, amount, D('0'), D('0'), D('0'), q.bid, False, 'insufficient_top_depth')
            px = q.bid * (D('1') - self.slippage_rate)
            notional = base_qty * px
            if notional < rules.min_notional:
                return LegResult(q.symbol, from_asset, to_asset, side, amount, D('0'), D('0'), D('0'), px, False, 'min_notional')
            gross = notional
            fee = gross * self.fee_rate
            out = gross - fee
            return LegResult(q.symbol, from_asset, to_asset, side, amount, gross, fee, out, px, True)

        if from_asset == q.quote and to_asset == q.base:
            side = 'BUY'
            px = q.ask * (D('1') + self.slippage_rate)
            raw_base_qty = amount / px
            base_qty = floor_step(raw_base_qty, rules.step_size)
            if base_qty < rules.min_qty:
                return LegResult(q.symbol, from_asset, to_asset, side, amount, D('0'), D('0'), D('0'), px, False, 'min_qty')
            if base_qty > q.ask_qty:
                return LegResult(q.symbol, from_asset, to_asset, side, amount, D('0'), D('0'), D('0'), px, False, 'insufficient_top_depth')
            spent = base_qty * px
            if spent < rules.min_notional:
                return LegResult(q.symbol, from_asset, to_asset, side, amount, D('0'), D('0'), D('0'), px, False, 'min_notional')
            gross = base_qty
            fee = gross * self.fee_rate
            out = gross - fee
            return LegResult(q.symbol, from_asset, to_asset, side, amount, gross, fee, out, px, True)

        return LegResult(q.symbol, from_asset, to_asset, 'INVALID', amount, D('0'), D('0'), D('0'), D('0'), False, 'asset_pair_mismatch')

    def evaluate_cycle(self, start_amount: Decimal, assets: Tuple[str, str, str, str], quotes: Tuple[Quote, Quote, Quote], rules: Tuple[SymbolRules, SymbolRules, SymbolRules], now_ms: Optional[int] = None) -> CycleResult:
        if assets[0] != assets[-1]:
            raise ValueError('cycle must start and end in same asset')
        now_ms = int(time.time() * 1000) if now_ms is None else now_ms
        freshness_error = self._fresh(list(quotes), now_ms)
        if freshness_error:
            return CycleResult(assets, [], start_amount, start_amount, D('0'), D('0'), D('0'), False, freshness_error)

        amount = start_amount
        legs: List[LegResult] = []
        for i in range(3):
            leg = self.execute_leg(amount, assets[i], assets[i+1], quotes[i], rules[i])
            legs.append(leg)
            if not leg.ok:
                return CycleResult(assets, legs, start_amount, amount, D('0'), D('0'), D('0'), False, leg.reject_reason)
            amount = leg.output_after_fee

        gross_amount = start_amount
        for i, q in enumerate(quotes):
            fa, ta = assets[i], assets[i+1]
            if fa == q.base and ta == q.quote:
                gross_amount = gross_amount * q.bid
            elif fa == q.quote and ta == q.base:
                gross_amount = gross_amount / q.ask
            else:
                gross_amount = D('0')
                break
        gross_pct = (gross_amount / start_amount - D('1')) * D('100') if start_amount else D('0')
        net_pct = (amount / start_amount - D('1')) * D('100') if start_amount else D('0')
        return CycleResult(assets, legs, start_amount, amount, gross_pct, net_pct, amount - start_amount, True)
