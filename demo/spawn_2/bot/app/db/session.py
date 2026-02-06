from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


def create_engine(database_url: str):
    return create_async_engine(
        database_url,
        pool_pre_ping=True,
        future=True,
    )


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
