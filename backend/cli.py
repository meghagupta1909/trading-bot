#!/usr/bin/env python3
"""
Binance Futures Trading Bot — Command Line Interface
Usage:
    python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python cli.py place-order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3200
    python cli.py place-order --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 65000 --stop-price 64500
    python cli.py health
    python cli.py recent-logs
"""
from __future__ import annotations

import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Ensure backend root is on path when run as a script
sys.path.insert(0, str(Path(__file__).parent))

from app.core.logging_config import setup_logging
from app.services.order_service import check_connectivity, place_order
from app.utils.log_utils import read_recent_logs

# Initialise logging
setup_logging()

app = typer.Typer(
    name="trading-bot",
    help="🤖 Binance Futures Testnet Trading Bot CLI",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _print_success(msg: str) -> None:
    rprint(f"[bold green]✅ {msg}[/bold green]")


def _print_error(msg: str) -> None:
    rprint(f"[bold red]❌ {msg}[/bold red]")


def _print_warning(msg: str) -> None:
    rprint(f"[bold yellow]⚠️  {msg}[/bold yellow]")


def _print_info(msg: str) -> None:
    rprint(f"[cyan]ℹ️  {msg}[/cyan]")


def _render_order_table(order: dict) -> None:
    table = Table(title="Order Details", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    fields = [
        ("Order ID", "orderId"),
        ("Client Order ID", "clientOrderId"),
        ("Symbol", "symbol"),
        ("Side", "side"),
        ("Type", "type"),
        ("Status", "status"),
        ("Quantity (orig)", "origQty"),
        ("Executed Qty", "executedQty"),
        ("Avg Price", "avgPrice"),
        ("Price", "price"),
        ("Stop Price", "stopPrice"),
        ("Time In Force", "timeInForce"),
    ]

    for label, key in fields:
        val = order.get(key)
        if val is not None and val != "" and val != "0":
            table.add_row(label, str(val))

    console.print(table)


def _render_summary_panel(summary: dict) -> None:
    lines = "\n".join(f"  [cyan]{k}[/cyan]: [white]{v}[/white]" for k, v in summary.items())
    rprint(Panel(lines, title="📋 Order Request Summary", border_style="blue"))


# ── Commands ───────────────────────────────────────────────────────────────────

@app.command("place-order")
def place_order_cmd(
    symbol: str = typer.Option(
        ..., "--symbol", "-s", help="Trading pair (e.g. BTCUSDT)", prompt="Symbol"
    ),
    side: str = typer.Option(
        ..., "--side", help="BUY or SELL", prompt="Side (BUY/SELL)"
    ),
    order_type: str = typer.Option(
        ..., "--type", "-t", help="MARKET, LIMIT, or STOP_LIMIT", prompt="Order type"
    ),
    quantity: float = typer.Option(
        ..., "--quantity", "-q", help="Order quantity", prompt="Quantity"
    ),
    price: Optional[float] = typer.Option(
        None, "--price", "-p", help="Limit price (required for LIMIT/STOP_LIMIT)"
    ),
    stop_price: Optional[float] = typer.Option(
        None, "--stop-price", help="Stop trigger price (required for STOP_LIMIT)"
    ),
    time_in_force: str = typer.Option("GTC", "--tif", help="Time in force: GTC/IOC/FOK"),
    reduce_only: bool = typer.Option(False, "--reduce-only", help="Reduce position only"),
) -> None:
    """
    [bold]Place a Futures order on Binance Testnet.[/bold]

    Examples:\n
      [green]Market buy 0.01 BTC:[/green]\n
        python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n
      [green]Limit sell 0.1 ETH at $3200:[/green]\n
        python cli.py place-order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3200\n
      [green]Stop-Limit buy BTC:[/green]\n
        python cli.py place-order --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 65000 --stop-price 64500
    """
    console.rule("[bold blue]Binance Futures Trading Bot[/bold blue]")

    async def _run() -> None:
        result = await place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(price)) if price else None,
            stop_price=Decimal(str(stop_price)) if stop_price else None,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
        )

        _render_summary_panel(result["request_summary"])

        if result["success"]:
            _print_success(result["message"])
            if result.get("order"):
                _render_order_table(result["order"])
        else:
            _print_error(result["message"])
            if result.get("error"):
                rprint(f"[red]Details: {result['error']}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_run())


@app.command("health")
def health_cmd() -> None:
    """Check connectivity to Binance Futures Testnet."""
    console.rule("[bold blue]Health Check[/bold blue]")

    async def _run() -> None:
        result = await check_connectivity()
        if result.get("connected"):
            _print_success("Binance Futures Testnet is reachable")
            _print_info(f"Server time: {result.get('server_time')}")
        else:
            _print_error("Cannot reach Binance Futures Testnet")
            _print_warning(f"Error: {result.get('error')}")
            raise typer.Exit(code=1)

    asyncio.run(_run())


@app.command("recent-logs")
def recent_logs_cmd(
    log_file: str = typer.Option("trading_bot.log", "--file", "-f", help="Log filename"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of tail lines"),
) -> None:
    """Display recent log entries."""
    console.rule(f"[bold blue]Recent Logs — {log_file}[/bold blue]")

    data = read_recent_logs(log_file=log_file, lines=lines)
    if not data["lines"]:
        _print_warning("No log entries found.")
        return

    for line in data["lines"]:
        if " | ERROR" in line or " | CRITICAL" in line:
            rprint(f"[red]{line}[/red]")
        elif " | WARNING" in line:
            rprint(f"[yellow]{line}[/yellow]")
        elif " | INFO" in line:
            rprint(f"[white]{line}[/white]")
        else:
            rprint(f"[dim]{line}[/dim]")

    _print_info(f"Showing last {len(data['lines'])} of {data['total_lines']} total lines")


if __name__ == "__main__":
    app()