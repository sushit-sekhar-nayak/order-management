# inventory/models.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# SQLite database file
DATABASE_URL = "sqlite:///inventory.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0.0)

    def as_dict(self):
        return {
            "sku": self.sku,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }

    def save(self):
        db_session.add(self)
        db_session.commit()

    @classmethod
    def create(cls, sku, name, quantity, price=0.0):
        p = cls(sku=sku, name=name, quantity=quantity, price=price)
        db_session.add(p)
        db_session.commit()
        return p

    @classmethod
    def get_by_sku(cls, sku):
        return db_session.query(cls).filter_by(sku=sku).first()

def init_db():
    Base.metadata.create_all(bind=engine)