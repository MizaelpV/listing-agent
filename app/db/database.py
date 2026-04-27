import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Missing required value: DATABASE_URL")


engine = create_async_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    class_=AsyncSession,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()