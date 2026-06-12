"""
Binance Futures Testnet REST client.
Handles authentication (HMAC-SHA256), request signing, and raw HTTP calls.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000  # milliseconds


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, status_code: int, code: int, msg: str):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        super().__init__(f"[HTTP {status_code}] Binance API error {code}: {msg}")


class BinanceFuturesClient:
    """
    Thin wrapper around the Binance USDT-M Futures REST API (testnet).

    Responsibilities:
    - sign requests with HMAC-SHA256
    - attach API-Key header
    - raise structured errors on non-2xx responses
    - log every outgoing request and incoming response at DEBUG level
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceFuturesClient initialised with base URL: %s", self._base_url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params)
        return hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self._base_url}{endpoint}"
        params = params or {}

        if signed:
            params["timestamp"] = self._timestamp()
            params["recvWindow"] = RECV_WINDOW
            params["signature"] = self._sign(params)

        logger.debug("REQUEST  %s %s | params: %s", method.upper(), endpoint, params)

        try:
            if method.upper() in ("GET", "DELETE"):
                response = self._session.request(method, url, params=params, timeout=10)
            else:
                response = self._session.request(method, url, data=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error reaching %s: %s", url, exc)
            raise ConnectionError(
                f"Could not connect to Binance Testnet ({url}). "
                "Check your internet connection."
            ) from exc
        except requests.exceptions.Timeout:
            logger.error("Request to %s timed out.", url)
            raise TimeoutError(f"Request to {url} timed out after 10 s.") from None

        logger.debug(
            "RESPONSE %s %s | status: %s | body: %s",
            method.upper(),
            endpoint,
            response.status_code,
            response.text[:500],
        )

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response from %s: %s", url, response.text[:200])
            response.raise_for_status()
            raise

        if not response.ok:
            code = data.get("code", -1)
            msg = data.get("msg", response.text)
            logger.error("API error | code=%s | msg=%s", code, msg)
            raise BinanceClientError(response.status_code, code, msg)

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> Dict[str, Any]:
        """Fetch server time — useful for connectivity checks."""
        return self._request("GET", "/fapi/v1/time")

    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Fetch exchange metadata; optionally filter by symbol."""
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/fapi/v1/exchangeInfo", params=params)

    def new_order(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Place a new order.
        kwargs are passed directly as order parameters (symbol, side, type, …).
        """
        return self._request("POST", "/fapi/v1/order", params=kwargs, signed=True)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Query the status of an existing order."""
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an open order by order ID."""
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    def get_account(self) -> Dict[str, Any]:
        """Return account information including balances."""
        return self._request("GET", "/fapi/v2/account", signed=True)
