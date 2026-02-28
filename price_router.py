from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal
from models import Product, ProductPrice, PriceAlert
from schemas import PriceUpdate
from fastapi import HTTPException

router = APIRouter(prefix="/prices", tags=["Price System"])

ALERT_THRESHOLD = 10  # percent


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_percentage(old_price, new_price):
    if old_price == 0 or old_price is None:
        return 0
    return ((new_price - old_price) / old_price) * 100


def send_notification(product_name, percentage):
    if percentage > 0:
        print(f"🔔 ALERT: {product_name} price increased by {percentage:.2f}%")
    else:
        print(f"🔔 ALERT: {product_name} price dropped by {abs(percentage):.2f}%")

    # Later connect this to voice/SMS


# ✅ Update Price
@router.post("/update")
def update_price(data: PriceUpdate, db: Session = Depends(get_db)):

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get last price
    last_price_entry = (
        db.query(ProductPrice)
        .filter(ProductPrice.product_id == data.product_id)
        .order_by(desc(ProductPrice.recorded_at))
        .first()
    )

    old_price = last_price_entry.price_per_kg if last_price_entry else None
    percentage = calculate_percentage(old_price, data.new_price)

    # Save new price
    new_price_entry = ProductPrice(
        product_id=data.product_id,
        price_per_kg=data.new_price
    )
    db.add(new_price_entry)
    db.commit()

    # Check sudden change
    if old_price and abs(percentage) >= ALERT_THRESHOLD:

        alert_type = "RAISE" if percentage > 0 else "DROP"

        alert = PriceAlert(
            product_id=data.product_id,
            old_price=old_price,
            new_price=data.new_price,
            percentage_change=percentage,
            alert_type=alert_type
        )

        db.add(alert)
        db.commit()

        send_notification(product.name, percentage)

    return {
        "message": "Price updated",
        "percentage_change": round(percentage, 2)
    }


# ✅ Get Current Prices
@router.get("/current")
def get_current_prices(db: Session = Depends(get_db)):

    products = db.query(Product).all()
    result = []

    for product in products:

        prices = (
            db.query(ProductPrice)
            .filter(ProductPrice.product_id == product.id)
            .order_by(desc(ProductPrice.recorded_at))
            .limit(2)
            .all()
        )

        if not prices:
            continue

        current_price = prices[0].price_per_kg
        previous_price = prices[1].price_per_kg if len(prices) > 1 else None

        percentage = calculate_percentage(previous_price, current_price)

        trend = "UP" if percentage > 0 else "DOWN" if percentage < 0 else "STABLE"

        result.append({
            "product": product.name,
            "current_price": current_price,
            "percentage_change": round(percentage, 2),
            "trend": trend
        })

    return result

@router.post("/add-product")
def add_product(name: str, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.name == name).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")

    new_product = Product(name=name)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product added successfully"}