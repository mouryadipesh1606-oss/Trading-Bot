"""
CLI entry point.
Parses arguments, validates input, invokes the order layer, and prints results.
"""

from __future__ import annotations

import argparse
import os
import sys
import logging

from .client import BinanceFuturesClient, BinanceClientError
from .logging_config import setup_logging
from .orders import (
    place_market_order,
    place_limit_order,
    place_stop_limit_order,
    format_order_response,
)
from .validators import validate_order_inputs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description=(
            "Place orders on Binance USDT-M Futures Testnet.\n"
            "API credentials are read from env vars BINANCE_API_KEY and BINANCE_API_SECRET."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Market buy 0.01 BTC:
    python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

  Limit sell 0.01 BTC at $65,000:
    python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000

  Stop-limit buy 0.01 BTC (trigger $62k, limit $62.1k):
    python -m bot.cli --symbol BTCUSDT --side BUY --type STOP_LIMIT \\
        --quantity 0.01 --stop-price 62000 --price 62100
""",
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT"],
        type=str.upper,
        help="Order type: MARKET, LIMIT, or STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity (e.g. 0.01)",
    )
    parser.add_argument(
        "--price",
        default=None,
        help="Limit price — required for LIMIT and STOP_LIMIT orders",
    )
    parser.add_argument(
        "--stop-price",
        default=None,
        dest="stop_price",
        help="Stop trigger price — required for STOP_LIMIT orders",
    )
    parser.add_argument(
        "--log-dir",
        default="logs",
        help="Directory for log files (default: logs/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print order summary without sending to the API",
    )
    return parser


def _print_request_summary(params: dict) -> None:
    print()
    print("=" * 52)
    print("  ORDER REQUEST SUMMARY")
    print("=" * 52)
    print(f"  Symbol        : {params['symbol']}")
    print(f"  Side          : {params['side']}")
    print(f"  Type          : {params['order_type']}")
    print(f"  Quantity      : {params['quantity']}")
    if params.get("price"):
        print(f"  Price         : {params['price']}")
    if params.get("stop_price"):
        print(f"  Stop Price    : {params['stop_price']}")
    print("=" * 52)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logger = setup_logging(args.log_dir)
    logger.debug("CLI args received: %s", vars(args))

    # --- Validate inputs ---
    try:
        params = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        print(f"\n[ERROR] Validation failed: {exc}", file=sys.stderr)
        logger.error("Input validation failed: %s", exc)
        return 1

    _print_request_summary(params)

    if args.dry_run:
        print("\n[DRY RUN] No order sent. Remove --dry-run to place the order.")
        logger.info("Dry run completed — no order sent.")
        return 0

    # --- Load API credentials ---
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        msg = (
            "Missing API credentials.\n"
            "Set the BINANCE_API_KEY and BINANCE_API_SECRET environment variables."
        )
        print(f"\n[ERROR] {msg}", file=sys.stderr)
        logger.error(msg)
        return 1

    # --- Create client and place order ---
    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

        order_type = params["order_type"]

        if order_type == "MARKET":
            response = place_market_order(
                client,
                symbol=params["symbol"],
                side=params["side"],
                quantity=params["quantity"],
            )
        elif order_type == "LIMIT":
            response = place_limit_order(
                client,
                symbol=params["symbol"],
                side=params["side"],
                quantity=params["quantity"],
                price=params["price"],
            )
        elif order_type == "STOP_LIMIT":
            response = place_stop_limit_order(
                client,
                symbol=params["symbol"],
                side=params["side"],
                quantity=params["quantity"],
                price=params["price"],
                stop_price=params["stop_price"],
            )
        else:
            # Should be unreachable given argparse choices
            raise ValueError(f"Unhandled order type: {order_type}")

    except BinanceClientError as exc:
        print(f"\n[FAILURE] API error: {exc}", file=sys.stderr)
        logger.error("Order placement failed (API): %s", exc)
        return 1
    except (ConnectionError, TimeoutError) as exc:
        print(f"\n[FAILURE] Network error: {exc}", file=sys.stderr)
        logger.error("Order placement failed (network): %s", exc)
        return 1
    except Exception as exc:
        print(f"\n[FAILURE] Unexpected error: {exc}", file=sys.stderr)
        logger.exception("Unexpected error during order placement")
        return 1

    # --- Print response ---
    print(format_order_response(response))
    print("\n[SUCCESS] Order placed successfully.\n")
    logger.info("Order placed successfully. orderId=%s", response.get("orderId"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
