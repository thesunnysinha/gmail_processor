import click
import logging
from core.db import SessionDep, Base, engine
from core.gmail_processor import GmailProcessor
from core.utils import get_rules

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@click.group(help="Gmail CLI tool for email processing. Use --help with any command to see details.")
def cli():
    pass

@cli.command(help="Run database migrations to create necessary tables.")
def migrate():
    logging.info("Running database migrations...")
    Base.metadata.create_all(engine)
    logging.info("Migrations completed successfully.")

@cli.command(help="Fetch emails from Gmail and store them in the database.")
def fetch():
    db = SessionDep()
    processor = GmailProcessor(db)
    processor.fetch_emails()
    db.close()

@cli.command(help="Apply filtering rules to stored emails.")
def applyrules():
    db = SessionDep()
    processor = GmailProcessor(db)
    rules = get_rules()
    processor.apply_rules(rules)
    db.close()

if __name__ == "__main__":
    cli()
