"""Command-line interface for The Gnarl Pi."""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import NoReturn, Optional

from gnarl import __version__
from gnarl.config import GnarlConfig
from gnarl.ui.controller import GnarlController

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = Path("/etc/gnarl/config.yaml")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_run(args: argparse.Namespace) -> int:
    """Run the Gnarl Pi synth.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    setup_logging(args.verbose)
    logger.info(f"Starting The Gnarl Pi v{__version__}")

    try:
        # Load configuration
        config_path = Path(args.config) if args.config else DEFAULT_CONFIG
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            return 1

        logger.info(f"Loading config from: {config_path}")
        config = GnarlConfig.from_yaml(config_path)

        # Initialize controller
        controller = GnarlController(config)
        controller.start()

        # Run until interrupted
        logger.info("Gnarl Pi is running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(0.1)
                controller.update()
        except KeyboardInterrupt:
            logger.info("Shutting down...")

        # Cleanup
        controller.stop()
        return 0

    except Exception as e:
        logger.error(f"Error running Gnarl Pi: {e}", exc_info=True)
        return 1


def cmd_test_hardware(args: argparse.Namespace) -> int:
    """Test hardware components.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    setup_logging(args.verbose)
    logger.info("Testing hardware components...")

    try:
        config_path = Path(args.config) if args.config else DEFAULT_CONFIG
        config = GnarlConfig.from_yaml(config_path)

        # Test each component
        from gnarl.hardware import LCDDisplay, RotaryEncoder, Switch

        # Test LCD
        if config.hardware.lcd:
            logger.info("Testing LCD...")
            lcd = LCDDisplay(config.hardware.lcd)
            lcd.write("Gnarl Pi", row=0, col=0)
            lcd.write("Test Mode", row=1, col=0)
            time.sleep(2)
            lcd.close()

        # Test encoders
        for i, enc_config in enumerate(config.hardware.encoders):
            logger.info(f"Testing encoder {i}: {enc_config.name}")
            encoder = RotaryEncoder(enc_config)
            encoder.on_change(lambda v: logger.info(f"Encoder value: {v}"))
            logger.info("Rotate encoder for 5 seconds...")
            time.sleep(5)
            encoder.close()

        # Test switches
        for i, sw_config in enumerate(config.hardware.switches):
            logger.info(f"Testing switch {i}: {sw_config.name}")
            switch = Switch(sw_config)
            switch.on_press(lambda: logger.info("Switch pressed!"))
            logger.info("Press switch for 5 seconds...")
            time.sleep(5)
            switch.close()

        logger.info("Hardware test complete!")
        return 0

    except Exception as e:
        logger.error(f"Hardware test failed: {e}", exc_info=True)
        return 1


def cmd_list_presets(args: argparse.Namespace) -> int:
    """List available presets.

    Args:
        args: Command-line arguments

    Returns:
        Exit code
    """
    setup_logging(args.verbose)

    try:
        config_path = Path(args.config) if args.config else DEFAULT_CONFIG
        config = GnarlConfig.from_yaml(config_path)

        print("\nAvailable Presets:")
        print("-" * 50)
        for i, preset in enumerate(config.presets):
            print(f"{i}: {preset.name}")
            if preset.description:
                print(f"   {preset.description}")
            print(f"   File: {preset.file}")
            print()

        return 0

    except Exception as e:
        logger.error(f"Failed to list presets: {e}")
        return 1


def main() -> NoReturn:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="The Gnarl Pi - Raspberry Pi Hardware Synthesizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the synthesizer")
    run_parser.add_argument(
        "-c", "--config", type=str, help=f"Config file (default: {DEFAULT_CONFIG})"
    )
    run_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    # Test hardware command
    test_parser = subparsers.add_parser("test-hardware", help="Test hardware components")
    test_parser.add_argument(
        "-c", "--config", type=str, help=f"Config file (default: {DEFAULT_CONFIG})"
    )
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    # List presets command
    list_parser = subparsers.add_parser("list-presets", help="List available presets")
    list_parser.add_argument(
        "-c", "--config", type=str, help=f"Config file (default: {DEFAULT_CONFIG})"
    )
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route to appropriate command
    commands = {
        "run": cmd_run,
        "test-hardware": cmd_test_hardware,
        "list-presets": cmd_list_presets,
    }

    exit_code = commands[args.command](args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
