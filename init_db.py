# init_db.py
from app.db import init_db
from app.models import processed_price_point, symbol_average, models, polling_job  # ensures models are registered

init_db()
