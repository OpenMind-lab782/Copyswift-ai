from payment_engine.database.database import Base, engine

# Import the model so SQLAlchemy registers it
from payment_engine.database.merchant_model import Merchant

Base.metadata.create_all(bind=engine)

print("✅ merchants table created successfully.")
