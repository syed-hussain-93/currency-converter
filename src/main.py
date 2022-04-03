import models
import requests
import json
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from models import CurrencyRates

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def dashboard(request: Request):
    """
    Displays dashboard to convert currency / homepage
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


def get_id(currency_from: str, currency_to: str):
    db = SessionLocal()
    id = (
        db.query(CurrencyRates.id)
        .filter_by(symbol_from=currency_from, symbol_to=currency_to)
        .all()[0][0]
    )
    db.close()
    return int(id)


def check_rate_request(currency_from: str, currency_to: str):
    db = SessionLocal()
    currency_rates_check = (
        db.query(CurrencyRates.id)
        .filter_by(symbol_from=currency_from, symbol_to=currency_to)
        .first()
    )
    db.close()
    return currency_rates_check


def fetch_rate(id: int):
    db = SessionLocal()
    conversion_row = db.query(CurrencyRates).filter(CurrencyRates.id == id).first()
    rate = conversion_row.rate
    db.close()
    return rate


@app.get("/currency_rate/{currency_from}/{currency_to}")
async def get_currency_rate(
    currency_from: str, currency_to: str, db: Session = Depends(get_db)
):

    # check if request is in table
    if not check_rate_request(currency_from, currency_to):
        # create conversion row in database

        currency_rates = CurrencyRates()
        currency_rates.symbol_from = currency_from
        currency_rates.symbol_to = currency_to
        response = requests.get(
            f"https://theforexapi.com/api/latest?base={currency_from}&symbols={currency_to}"
        )
        response_dict = json.loads(response.text)
        currency_rates.rate = response_dict["rates"][f"{currency_to}"]

        db.add(currency_rates)
        db.commit()

    id = get_id(currency_from, currency_to)
    rate = fetch_rate(id)
    return {"id": id, "From": currency_from, "To": currency_to, "Rate": rate}
