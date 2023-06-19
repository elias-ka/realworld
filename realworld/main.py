from dotenv import load_dotenv
from fastapi import FastAPI

from realworld.db import session
from realworld.db.base_class import Base

if __name__ == "__main__":
    load_dotenv()
    Base.metadata.create_all(bind=session.engine)
    app = FastAPI()
