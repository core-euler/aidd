from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


def create_engine_and_session(database_url: str):
    engine = create_engine(database_url, pool_pre_ping=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, session_local


def init_db(engine):
    Base.metadata.create_all(bind=engine)
