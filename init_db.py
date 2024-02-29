from database import engine, Base
from accounts.models import User
from orders.models import Orders


Base.metadata.create_all(bind=engine)