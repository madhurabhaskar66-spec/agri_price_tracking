from fastapi import FastAPI
from database import engine
from models import Base
from price_router import router as price_router
from apscheduler.schedulers.background import BackgroundScheduler
from price_fetcher import auto_update_prices

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(price_router)

scheduler = BackgroundScheduler()
scheduler.add_job(auto_update_prices, 'interval', minutes=1)  # 1 min for testing
scheduler.start()