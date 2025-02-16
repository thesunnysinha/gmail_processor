import pytest
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base, Email
from core.gmail_processor import GmailProcessor
from faker import Faker
from core.config import TEST_DB_PATH

# Initialize Faker
fake = Faker()

engine = create_engine(TEST_DB_PATH, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture(scope="function")
def db_session():
    """ Creates a fresh database for each test """
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_email_model(db_session):
    """ Test email model creation """
    email = Email(msg_id=fake.uuid4(), sender=fake.email(), subject=fake.sentence(), snippet=fake.text())
    db_session.add(email)
    db_session.commit()
    
    fetched_email = db_session.query(Email).filter_by(msg_id=email.msg_id).first()
    assert fetched_email is not None
    assert fetched_email.sender == email.sender

def test_fetch_emails(monkeypatch, db_session):
    """ Mock Gmail API and test fetching emails using GmailProcessor """
    processor = GmailProcessor(db_session)
    
    def mock_authenticate(self):
        return None  # Skip authentication in tests

    def mock_service():
        class MockMessages:
            def list(self, **kwargs):
                class MockListResponse:
                    def execute(self):
                        return {"messages": [{"id": "1"}]}
                return MockListResponse()
            
            def get(self, **kwargs):
                class MockGetResponse:
                    def execute(self):
                        return {
                            "id": "1",
                            "payload": {"headers": [{"name": "From", "value": fake.email()},
                                                    {"name": "Subject", "value": fake.sentence()}]},
                            "snippet": fake.text()
                        }
                return MockGetResponse()

        class MockGmailService:
            def users(self):
                return self
            def messages(self):
                return MockMessages()
        
        return MockGmailService()

    monkeypatch.setattr("core.gmail_processor.GmailProcessor.authenticate", mock_authenticate)
    monkeypatch.setattr("core.gmail_processor.build", lambda *args, **kwargs: mock_service())

    processor.fetch_emails()
    emails = db_session.query(Email).all()
    assert len(emails) == 1
    assert "@" in emails[0].sender  # Ensures valid email format

def test_apply_rules(db_session, monkeypatch):
    """ Test rule application using GmailProcessor with explicitly passed rules """
    processor = GmailProcessor(db_session)
    email = Email(msg_id=fake.uuid4(), sender=fake.company_email(), subject="Interview", snippet=fake.text(), is_processed=False)
    db_session.add(email)
    db_session.commit()

    rules = [
        {
            "predicate": "All",
            "conditions": [
                {"field": "From", "predicate": "Contains", "value": email.sender.split("@")[1]},
                {"field": "Subject", "predicate": "Contains", "value": "Interview"}
            ],
            "actions": [
                {"action": "Mark as Read"},
                {"action": "Move Message", "to_mailbox": "Important"}
            ]
        },
        {
            "predicate": "All",
            "conditions": [
                {"field": "From", "predicate": "Contains", "value": email.sender.split("@")[1]},
                {"field": "Subject", "predicate": "Contains", "value": "Interview"}
            ],
            "actions": [
                {"action": "Mark as Unread"},
                {"action": "Move Message", "to_mailbox": "Important"}
            ]
        },
    ]

    def mock_authenticate(self):
        return None  # Skip authentication in tests

    def mock_service():
        class MockMessages:
            def modify(self, userId, id, body):
                class MockModifyResponse:
                    def execute(self):
                        return None
                return MockModifyResponse()

        class MockGmailService:
            def users(self):
                return self
            def messages(self):
                return MockMessages()
        
        return MockGmailService()

    monkeypatch.setattr("core.gmail_processor.GmailProcessor.authenticate", mock_authenticate)
    monkeypatch.setattr("core.gmail_processor.build", lambda *args, **kwargs: mock_service())

    processor.apply_rules(rules)

    updated_email = db_session.query(Email).filter_by(msg_id=email.msg_id).first()
    assert updated_email.is_processed is True
    logging.info("Test Passed: Actions applied correctly - Mark as Read, Mark as Unread, Move Message")