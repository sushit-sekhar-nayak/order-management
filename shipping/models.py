# shipping/models.py
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

DATABASE_URL = "sqlite:///shipping.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class Shipping(Base):
    __tablename__ = 'shipping'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, nullable=False)
    items = Column(JSON, nullable=False)
    status = Column(String, default="PROCESSING")  # PROCESSING, SHIPPED

    def as_dict(self):
        return {
            "order_id": self.order_id,
            "items": self.items,
            "status": self.status
        }

    def save(self):
        db_session.add(self)
        db_session.commit()

    @classmethod
    def create(cls, order_id, items):
        s = cls(order_id=order_id, items=items)
        db_session.add(s)
        db_session.commit()
        return s

    @classmethod
    def get_by_order_id(cls, order_id):
        return db_session.query(cls).filter_by(order_id=order_id).first()

def init_db():
    Base.metadata.create_all(bind=engine)