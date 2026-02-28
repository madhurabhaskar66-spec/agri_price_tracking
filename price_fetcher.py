import requests
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Product, ProductPrice, PriceAlert
from datetime import datetime

API_KEY = "YOUR_NEW_API_KEY"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}?api-key={API_KEY}&format=json&limit=50"

ALERT_THRESHOLD = 10  # percent


def calculate_percentage(old_price, new_price):
    if not old_price or old_price == 0:
        return 0
    return ((new_price - old_price) / old_price) * 100


def auto_update_prices():
    print("Fetching mandi prices...")

    response = requests.get(URL)
    data = response.json()
    records = data.get("records", [])

    db: Session = SessionLocal()

    for item in records:
        commodity = item.get("commodity")
        modal_price = item.get("modal_price")

        if not commodity or not modal_price:
            continue

        modal_price = float(modal_price)

        # Case-insensitive product match
        product = db.query(Product).filter(
            func.lower(Product.name) == commodity.lower()
        ).first()

        if not product:
            continue  # skip if product not in DB

        # Get last price
        last_price_entry = (
            db.query(ProductPrice)
            .filter(ProductPrice.product_id == product.id)
            .order_by(ProductPrice.recorded_at.desc())
            .first()
        )

        old_price = last_price_entry.price_per_kg if last_price_entry else None
        percentage = calculate_percentage(old_price, modal_price)

        # Save new price
        new_price_entry = ProductPrice(
            product_id=product.id,
            price_per_kg=modal_price,
            recorded_at=datetime.utcnow()
        )

        db.add(new_price_entry)
        db.commit()

        # Alert check
        if old_price and abs(percentage) >= ALERT_THRESHOLD:
            alert_type = "RAISE" if percentage > 0 else "DROP"

            alert = PriceAlert(
                product_id=product.id,
                old_price=old_price,
                new_price=modal_price,
                percentage_change=percentage,
                alert_type=alert_type,
                created_at=datetime.utcnow()
            )

            db.add(alert)
            db.commit()

            print(f"🔔 ALERT: {product.name} changed by {percentage:.2f}%")

    db.close()
    print("Auto update completed.")