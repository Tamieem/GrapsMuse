# database/db_utils.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import NoResultFound
from database.models import Base, Promotion
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False, future=True)
Session = scoped_session(sessionmaker(bind=engine))


def get_session():
    """Returns a new SQLAlchemy session."""
    return Session()


def init_db():
    """Create tables based on models."""
    Base.metadata.create_all(engine)


def get_or_create_promotion(session, name: str) -> Promotion:
    """Gets an existing promotion by name, or creates it."""
    try:
        promotion = session.query(Promotion).filter_by(name=name).one()
    except NoResultFound:
        promotion = Promotion(name=name)
        session.add(promotion)
        session.commit()
        session.refresh(promotion)
    return promotion
