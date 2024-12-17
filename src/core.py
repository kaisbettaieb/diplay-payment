import uuid
from typing import List, Dict, Optional

import requests
import pandas as pd

currencies = {
    "EUR": "euro",
    "USD": "dollars"
}

gender = {
    1: "Female",
    2: "Male"
}


class Observer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Observer, cls).__new__(cls, *args, **kwargs)
            cls._instance.records = []
        return cls._instance

    def add(self, msg: str, level: str, **kwargs):
        """
        Add new message to the error observer
        :param msg: str, the message to add
        :param kwargs: additional details to append to the message, such as customer_id, date, ect..
        :return: None
        """
        self.records.append({
            "id": str(uuid.uuid4()),
            "message": msg,
            "level": level,
            "additional": kwargs

        })

    def report(self):
        """
        Print all the records, could potentially send the records to a logging central system
        :return:
        """
        if self.records:
            for record in self.records:
                print(
                    f"ID: {record['id']} | level: {record["level"].upper()} | message: {record["message"]} | {record.get('additional')} ")


def create_bills(customers_details: pd.DataFrame, purchases_by_customers: Dict[int, list], observer: Observer):
    """
    Create and return a list of bills of purchases of customers

    Customers that are missing critial information such as email, firstname, lastname and title will be ignored

    Customers  with no purchases will be ignored
    :param customers_details: a DataFrame of customers details
    :param purchases_by_customers: a Dict where keys are customer_id and values are the list of purchases
    :param observer: an Observer object to hold the logging messages
    :return: A list of dicts of bills
    """
    bill = []
    for customer in customers_details.itertuples(index=False):
        customer_id = customer.customer_id

        if (pd.isna(customer.email)
                or pd.isna(customer.firstname)
                or pd.isna(customer.lastname)
                or pd.isna(customer.title)
        ):
            observer.add(f"A customer {customer_id} is missing some details, can't process their purchases",
                         level="error", customer_id=customer_id)
            continue
        if not purchases_by_customers.get(customer_id):
            observer.add(f"A customer {customer_id} will be ignored because they don't have any purchases",
                         level="debug", customer_id=customer_id)
            continue
        bill.append({
            "salutation": gender[customer.title],
            "last_name": customer.lastname,
            "first_name": customer.firstname,
            "email": customer.email,
            "purchases": purchases_by_customers.get(customer_id, [])
        })
    return bill


def map_purchases(customers: pd.DataFrame,
                  purchases: pd.DataFrame,
                  observer: Observer) -> Optional[Dict[int, list]]:
    """
    Map for each customers the details of each of their purchases
    :param customers: a DataFrame containing details about customers
    :param purchases: a DataFrame containing details about the purchases
    :param observer: Observer , an object to hold records of issues
    :return: dict : where customer_id are the keys and the values are list of purchases
    """
    if customers.empty:
        observer.add(
            f"Failed to map purchases to customers, because no customer was found in data.", level="debug")
        return

    customers_purchases = customers.merge(
        purchases, on="customer_id", how="left"
    )
    purchases_by_customer_id = {}

    for row in customers_purchases.itertuples(index=False):
        customer_id = row.customer_id
        if customer_id not in purchases_by_customer_id:
            purchases_by_customer_id[customer_id] = []
        try:
            purchases_by_customer_id[customer_id].append({
                "product_id": row.product_id,
                "price": float(row.price),
                "currency": currencies[row.currency],
                "quantity": int(row.quantity),
                "purchased_at": row.date
            })
        except KeyError:
            observer.add(f"Failed to map a purchase to costumer with id {customer_id}", level="debug")
            continue

    return purchases_by_customer_id


def send_bills(purchase_history: List[dict], url: str, observer: Observer, **kwargs) -> bool:
    """
    Send the purchase bills of customers to api endpoint through a HTTP PUT request

    :param purchase_history: List[dict] of customer's purchases
    :param url: url to Display endpoint
    :param observer: Observer, the class to hold records
    :param kwargs: additional parameters to pass with the request
    :return: bool, True if correctly sent else False
    """
    try:
        request = requests.put(
            url, json=purchase_history, **kwargs
        )
        if request.ok:
            return True
        observer.add(f"Failed to send invoice, http status code {request.status_code}, error: {request.content}",
                     level="error")
        return False
    except requests.RequestException as e:
        observer.add(f"Failed to send invoice, make sure the url provided is correct and there is internet connection",
                     level="error", error=str(e))
        return False
