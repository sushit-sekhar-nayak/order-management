# order/models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import json

DATABASE_URL = "sqlite:///order.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, nullable=False)
    items = Column(JSON, nullable=False)  # [{"sku":"A101","qty":2}, ...]
    total_amount = Column(Float, default=0.0)
    status = Column(String, default="PENDING")  # PENDING, SHIPPED, etc.

    def as_dict(self):
        return {
            "order_id": self.order_id,
            "items": self.items,
            "total_amount": self.total_amount,
            "status": self.status
        }

    def save(self):
        db_session.add(self)
        db_session.commit()

    @classmethod
    def create(cls, order_id, items, total_amount):
        o = cls(order_id=order_id, items=items, total_amount=total_amount)
        db_session.add(o)
        db_session.commit()
        return o

    @classmethod
    def get_by_order_id(cls, order_id):
        return db_session.query(cls).filter_by(order_id=order_id).first()

def init_db():
    Base.metadata.create_all(bind=engine)