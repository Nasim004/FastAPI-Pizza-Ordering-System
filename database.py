from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base


SQL_ALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/database_name"
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)
Session = sessionmaker(autoflush=True,bind=engine)
Base = declarative_base()