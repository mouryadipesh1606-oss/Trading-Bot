"""
Input validation helpers.
All functions raise ValueError with a human-readable message on failure.
"""

from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Return uppercased symbol or raise ValueError."""
    symbol = symbol.strip().upper()
    if not symbol.isalpha() or len(symbol) < 3:
        raise ValueError(
            f"Invalid symbol '{symbol}'. Expected alphabetic string like BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    """Return uppercased side or raise ValueError."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Return uppercased order type or raise ValueError."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str) -> Decimal:
    """Parse and validate quantity; must be positive."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price: Optional[str]) -> Optional[Decimal]:
    """Parse and validate price when provided; must be positive."""
    if price is None:
        return None
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than zero, got {p}.")
    return p


def validate_stop_price(stop_price: Optional[str]) -> Optional[Decimal]:
    """Parse and validate stop price when provided."""
    return validate_price(stop_price)


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """
    Run all validations and return a clean dict of parsed values.
    Raises ValueError on the first validation failure found.
    """
    order_type_clean = validate_order_type(order_type)

    if order_type_clean == "LIMIT" and price is None:
        raise ValueError("A price is required for LIMIT orders.")

    if order_type_clean == "STOP_LIMIT" and (price is None or stop_price is None):
        raise ValueError("Both --price and --stop-price are required for STOP_LIMIT orders.")

    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": order_type_clean,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price),
        "stop_price": validate_stop_price(stop_price),
    }
