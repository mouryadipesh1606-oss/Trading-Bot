"""
Order placement logic.
Sits between the CLI layer and the raw API client.
Translates validated user input into API calls and formats the response.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from .client import BinanceFuturesClient

logger = logging.getLogger("trading_bot.orders")

# Time-in-force constants
TIF_GTC = "GTC"  # Good Till Cancelled


def _fmt(value: Any, decimals: int = 8) -> str:
    """Format a numeric value for Binance (strip trailing zeros)."""
    if value is None:
        return ""
    d = Decimal(str(value))
    # Binance expects plain decimal strings like "0.001", not "1E-3"
    return f"{d:.{decimals}f}".rstrip("0").rstrip(".")


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
) -> Dict[str, Any]:
    """
    Place a MARKET order on USDT-M Futures.

    Returns the raw API response dict.
    """
    logger.info(
        "Placing MARKET order | symbol=%s | side=%s | qty=%s",
        symbol,
        side,
        quantity,
    )

    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": _fmt(quantity),
    }

    response = client.new_order(**params)
    logger.info("MARKET order placed | orderId=%s | status=%s", response.get("orderId"), response.get("status"))
    return response


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    time_in_force: str = TIF_GTC,
) -> Dict[str, Any]:
    """
    Place a LIMIT order on USDT-M Futures.

    Returns the raw API response dict.
    """
    logger.info(
        "Placing LIMIT order | symbol=%s | side=%s | qty=%s | price=%s | tif=%s",
        symbol,
        side,
        quantity,
        price,
        time_in_force,
    )

    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": _fmt(quantity),
        "price": _fmt(price),
        "timeInForce": time_in_force,
    }

    response = client.new_order(**params)
    logger.info("LIMIT order placed | orderId=%s | status=%s", response.get("orderId"), response.get("status"))
    return response


def place_stop_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    stop_price: Decimal,
    time_in_force: str = TIF_GTC,
) -> Dict[str, Any]:
    """
    Place a STOP_LIMIT (STOP) order on USDT-M Futures.

    The order triggers when the market reaches `stop_price`,
    then posts a limit order at `price`.

    Returns the raw API response dict.
    """
    logger.info(
        "Placing STOP_LIMIT order | symbol=%s | side=%s | qty=%s | price=%s | stopPrice=%s",
        symbol,
        side,
        quantity,
        price,
        stop_price,
    )

    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",          # Binance Futures uses "STOP" for stop-limit
        "quantity": _fmt(quantity),
        "price": _fmt(price),
        "stopPrice": _fmt(stop_price),
        "timeInForce": time_in_force,
    }

    response = client.new_order(**params)
    logger.info(
        "STOP_LIMIT order placed | orderId=%s | status=%s",
        response.get("orderId"),
        response.get("status"),
    )
    return response


def format_order_response(response: Dict[str, Any]) -> str:
    """
    Return a nicely formatted multi-line string summarising an order response.
    """
    avg_price = response.get("avgPrice", "0")
    avg_price_str = avg_price if float(avg_price) > 0 else "N/A (pending fill)"

    lines = [
        "",
        "=" * 52,
        "  ORDER RESPONSE",
        "=" * 52,
        f"  Order ID      : {response.get('orderId', 'N/A')}",
        f"  Client Ord ID : {response.get('clientOrderId', 'N/A')}",
        f"  Symbol        : {response.get('symbol', 'N/A')}",
        f"  Side          : {response.get('side', 'N/A')}",
        f"  Type          : {response.get('type', 'N/A')}",
        f"  Status        : {response.get('status', 'N/A')}",
        f"  Orig Qty      : {response.get('origQty', 'N/A')}",
        f"  Executed Qty  : {response.get('executedQty', 'N/A')}",
        f"  Avg Price     : {avg_price_str}",
        f"  Price         : {response.get('price', 'N/A')}",
        f"  Time-in-Force : {response.get('timeInForce', 'N/A')}",
        f"  Update Time   : {response.get('updateTime', 'N/A')}",
        "=" * 52,
    ]
    return "\n".join(lines)
