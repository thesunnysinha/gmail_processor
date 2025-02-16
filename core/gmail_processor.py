import os
import base64
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from core.db import SessionDep
from core.models import Email
from core.config import SCOPES, TOKEN_FILE, CREDENTIALS_FILE
from core.schema import EmailSchema

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GmailProcessor:
    """Class-based implementation of Gmail email fetching & rule application."""

    def __init__(self, db: SessionDep):
        self.db: Session = db
        self.creds: Credentials | None = None

    def authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth 2.0."""
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_FILE}. Please provide a valid file.")

        if os.path.exists(TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
            except Exception as e:
                logging.error(f"Error loading credentials from token file: {e}")
                os.remove(TOKEN_FILE)
                self.creds = None

        if not self.creds or not self.creds.valid:
            logging.warning("Token file not found or invalid. A new authentication flow will be initiated.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            self.creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, "wb") as token:
                token.write(self.creds.to_json().encode())

    def fetch_emails(self) -> None:
        """Fetch emails from Gmail and store them in SQLite3."""
        try:
            self.authenticate()
            service = build("gmail", "v1", credentials=self.creds)
            results = service.users().messages().list(userId="me", maxResults=10).execute()
            messages = results.get("messages", [])

            for msg in messages:
                msg_id = msg["id"]
                message = service.users().messages().get(userId="me", id=msg_id).execute()
                headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}
                snippet = base64.urlsafe_b64decode(message.get("snippet", "").encode()).decode(errors="ignore")

                email_data = EmailSchema(
                    msg_id=msg_id,
                    sender=headers.get("From", ""),
                    subject=headers.get("Subject", ""),
                    snippet=snippet,
                    received_at=datetime.now(timezone.utc),
                    is_processed=False,
                )

                existing_email = self.db.query(Email).filter(Email.msg_id == msg_id).first()
                if not existing_email:
                    new_email = Email(**email_data.model_dump())
                    self.db.add(new_email)

            self.db.commit()
            logging.info("Emails successfully fetched and stored.")
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")

    def apply_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Apply filtering rules stored in JSON and update Gmail accordingly."""
        try:
            self.authenticate()
            service = build("gmail", "v1", credentials=self.creds)
            emails = self.db.query(Email).filter(Email.is_processed == False).all()
            
            for email in emails:
                for rule in rules:
                    conditions_met = []
                    field_mappings = {
                        "From": email.sender,
                        "Subject": email.subject,
                        "Message": email.snippet,
                        "Date Received": email.received_at,
                    }
                    
                    for condition in rule["conditions"]:
                        field_value = field_mappings.get(condition["field"], "")
                        if isinstance(field_value, datetime):
                            field_value = (datetime.now(timezone.utc) - field_value).days

                        match condition["predicate"]:
                            case "Contains" if condition["value"] in str(field_value):
                                conditions_met.append(True)
                            case "Does not Contain" if condition["value"] not in str(field_value):
                                conditions_met.append(True)
                            case "Equals" if condition["value"] == str(field_value):
                                conditions_met.append(True)
                            case "Does not Equal" if condition["value"] != str(field_value):
                                conditions_met.append(True)
                            case "Less than" if isinstance(field_value, int) and field_value < int(condition["value"]):
                                conditions_met.append(True)
                            case "Greater than" if isinstance(field_value, int) and field_value > int(condition["value"]):
                                conditions_met.append(True)
                            case _:
                                conditions_met.append(False)
                    
                    if (rule["predicate"] == "All" and all(conditions_met)) or (rule["predicate"] == "Any" and any(conditions_met)):
                        logging.info(f"Applying actions for email: {email.subject}")
                        msg_labels = {"removeLabelIds": [], "addLabelIds": []}
                        for action in rule["actions"]:
                            match action["action"]:
                                case "Mark as Read":
                                    msg_labels["removeLabelIds"].append("UNREAD")
                                    logging.info("Marked as read")
                                case "Mark as Unread":
                                    msg_labels["addLabelIds"].append("UNREAD")
                                    logging.info("Marked as unread")
                                case "Move Message":
                                    msg_labels["addLabelIds"].append(action["to_mailbox"])
                                    logging.info(f"Moved to {action['to_mailbox']}")
                        
                        service.users().messages().modify(
                            userId="me", id=email.msg_id, body=msg_labels
                        ).execute()
                        
                        email.is_processed = True
            
            self.db.commit()
            logging.info("Rules applied successfully to Gmail and local DB.")
        except Exception as e:
            logging.error(f"Error applying rules: {e}")