import argparse
from pathlib import Path

from src.ingestion import ingest
from src.grant_answering import process_grant
from src.utils.configs import AppConfig

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Catalyzator CLI tool for ingestion and grant answering"
    )
    
    # Config source arguments
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--config",
        type=Path,
        help="Path to JSON config file"
    )
    
    # Command subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Command to execute"
    )
    
    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest innovator data"
    )
    ingest_parser.add_argument(
        "entity_id",
        help="ID of the entity to ingest"
    )
    ingest_parser.add_argument(
        "--form-id",
        default="innovator_introduction",
        type=str,
        choices=["innovator_introduction"],
        help="Form ID to collect (default: innovator_introduction)"
    )
    
    # Answer command
    answer_parser = subparsers.add_parser(
        "answer",
        help="Generate grant answers"
    )
    answer_parser.add_argument(
        "entity_id",
        help="ID of the entity to generate answers for"
    )
    
    return parser.parse_args()

def load_config(args: argparse.Namespace) -> AppConfig:
    """Load configuration from specified source"""
    if args.config:
        return AppConfig.from_json(args.config)
    return AppConfig.from_env()

def main():
    """Main entry point"""
    args = parse_args()
    config = load_config(args)
    
    if args.command == "ingest":
        ingest(
            config=config,
            entity_id=args.entity_id,
            form_id=args.form_id
        )
    elif args.command == "answer":
        process_grant(
            config=config,
            entity_id=args.entity_id,
        )

if __name__ == "__main__":
    main()
