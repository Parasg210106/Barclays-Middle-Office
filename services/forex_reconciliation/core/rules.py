def check_rate_mismatch(trade_a, trade_b):
    return trade_a.get("FXRate") != trade_b.get("FXRate")

def check_amount_mismatch(trade_a, trade_b):
    return float(trade_a.get("NotionalAmount", 0)) != float(trade_b.get("NotionalAmount", 0))

def check_buy_sell_mismatch(trade_a, trade_b):
    return trade_a.get("Direction") != trade_b.get("Direction")

def check_currency_pair_mismatch(trade_a, trade_b):
    return trade_a.get("CurrencyPair") != trade_b.get("CurrencyPair")

def check_product_type_mismatch(trade_a, trade_b):
    return trade_a.get("ProductType") != trade_b.get("ProductType")

def check_settlement_date_mismatch(fo_trade, bo_trade):
    return fo_trade.get("SettlementDate") != bo_trade.get("SettlementDate")

def check_value_date_mismatch(fo_trade, bo_trade):
    return fo_trade.get("ValueDate") != bo_trade.get("ValueDate")

def check_fxrate_mismatch(fo_trade, bo_trade):
    return fo_trade.get("FXRate") != bo_trade.get("FXRate")
