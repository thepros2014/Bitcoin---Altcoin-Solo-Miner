#!/usr/bin/env python3
"""
Entry point for LittleMiner application.
This file is used when packaging the application as an executable.
"""

import sys
import os
import logging
import threading
import time
import webbrowser
import argparse
import json

import requests

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('littleminer.log', encoding='utf-8')
        ]
    )

def _open_docs_after_delay(url: str, delay_seconds: float = 1.5):
    """Open API docs in browser after a short delay (best effort)."""
    try:
        time.sleep(delay_seconds)
        webbrowser.open(url)
    except Exception:
        # Non-fatal: app should continue even if browser can't be opened.
        pass


def _get_api_base_url():
    from main import settings
    display_host = "127.0.0.1" if settings.api_host in ("0.0.0.0", "::") else settings.api_host
    return f"http://{display_host}:{settings.api_port}"


def _prompt_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Value cannot be empty.")


def _prompt_float(prompt_text: str, default: float = None) -> float:
    while True:
        raw = input(prompt_text).strip()
        if raw == "" and default is not None:
            return default
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")


def _prompt_hardware_type() -> str:
    allowed = {"cpu", "gpu", "asic"}
    while True:
        value = input("Hardware type (cpu/gpu/asic): ").strip().lower()
        if value in allowed:
            return value
        print("Invalid hardware type. Choose: cpu, gpu, or asic.")


def _print_json(data):
    print(json.dumps(data, indent=2, default=str))


def _api_get(path: str):
    base = _get_api_base_url()
    return requests.get(f"{base}{path}", timeout=20)


def _api_post(path: str, payload: dict):
    base = _get_api_base_url()
    return requests.post(f"{base}{path}", json=payload, timeout=20)


def run_cli_forms():
    print("\nLittleMiner Interactive CLI (Forms Mode)")
    print("This interface talks to the running API server.\n")

    while True:
        print("\n===== Main Menu =====")
        print("1) Start API server")
        print("2) Register miner")
        print("3) List miners")
        print("4) Get miner by ID")
        print("5) Profitability (all)")
        print("6) Profitability stats")
        print("7) Best profitability")
        print("8) Switch recommendation by miner ID")
        print("9) Exit")

        choice = input("Select an option [1-9]: ").strip()

        try:
            if choice == "1":
                print("Starting API server...")
                run_server()
                return
            elif choice == "2":
                wallet = _prompt_non_empty("Wallet address: ")
                hw_type = _prompt_hardware_type()
                hw_name = input("Hardware name [generic]: ").strip() or "generic"
                electricity_cost = _prompt_float("Electricity cost ($/kWh) [0.10]: ", default=0.10)
                min_profit_threshold = _prompt_float("Min profit threshold [0.05]: ", default=0.05)

                payload = {
                    "wallet_address": wallet,
                    "hardware_type": hw_type,
                    "hardware_name": hw_name,
                    "electricity_cost": electricity_cost,
                    "min_profit_threshold": min_profit_threshold
                }
                resp = _api_post("/miners", payload)
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "3":
                resp = _api_get("/miners")
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "4":
                miner_id = _prompt_non_empty("Miner ID: ")
                resp = _api_get(f"/miners/{miner_id}")
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "5":
                resp = _api_get("/profitability")
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "6":
                resp = _api_get("/profitability/stats")
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "7":
                resp = _api_get("/profitability/best")
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "8":
                miner_id = _prompt_non_empty("Miner ID: ")
                resp = _api_get(f"/profitability/switch-recommendation/{miner_id}")
                print(f"Status: {resp.status_code}")
                _print_json(resp.json())
            elif choice == "9":
                print("Exiting CLI forms mode.")
                return
            else:
                print("Invalid choice. Please select 1-9.")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            print("If API is not running, choose option 1 to start it.")
        except ValueError:
            print("Response parsing error. The server may have returned non-JSON output.")


def run_server():
    logger = logging.getLogger(__name__)

    import uvicorn
    from main import app, settings

    display_host = "127.0.0.1" if settings.api_host in ("0.0.0.0", "::") else settings.api_host
    base_url = f"http://{display_host}:{settings.api_port}"
    docs_url = f"{base_url}/docs"

    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")
    logger.info(f"Open API docs at: {docs_url}")
    print("\nLittleMiner is an API server (not a desktop GUI).")
    print(f"API docs: {docs_url}\n")

    threading.Thread(
        target=_open_docs_after_delay,
        args=(docs_url,),
        daemon=True
    ).start()

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )


def main():
    """Main entry point"""
    logger = None
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting LittleMiner application")

        parser = argparse.ArgumentParser(description="LittleMiner launcher")
        parser.add_argument(
            "--serve",
            action="store_true",
            help="Start API server directly (non-interactive mode)"
        )
        args = parser.parse_args()

        if args.serve:
            run_server()
        else:
            run_cli_forms()
    except KeyboardInterrupt:
        if logger:
            logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        if logger:
            logger.error(f"Application error: {e}", exc_info=True)
        else:
            print(f"Application error: {e}")
        sys.exit(1)
    finally:
        if logger:
            logger.info("LittleMiner application stopped")

if __name__ == "__main__":
    main()