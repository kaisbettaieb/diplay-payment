import pandas as pd
import pytest

from src.core import Observer, map_purchases, send_bills, create_bills


@pytest.fixture
def observer():
    Observer._instance = None
    return Observer()


@pytest.fixture
def customers_data():
    data = {
        "customer_id": [1, 2, 3, 4],
        "email": ["test@test.com", "test1@test.com", None, "test4@test.com"],
        "firstname": ["Test", "Test1", "Test2", "Test4"],
        "lastname": ["LastTest", "LastTest1", "LastTest2", "LastTest4"],
        "title": [1, 2, None, 1]
    }
    return pd.DataFrame(data)


@pytest.fixture
def purchases_data():
    return pd.DataFrame({
        "customer_id": [1, 5, 2],
        "product_id": [101, 102, 201],
        "quantity": [1, 2, 3],
        "price": [10.0, 20.0, 15.5],
        "currency": ["USD", "EUR", "USD"],
        "date": ["2024-12-15", "2024-12-17", "2024-12-17"]
    })


@pytest.fixture
def mapped_purchases():
    return {1: [
        {'product_id': 101, 'price': 10.0, 'currency': 'dollars', 'quantity': 1, 'purchased_at': '2024-12-15'},
    ],
        2: [
            {'product_id': 201, 'price': 15.5, 'currency': 'dollars', 'quantity': 3, 'purchased_at': '2024-12-17'}
        ],
        3: []
    }


def test_core_map_purchases_success(observer, purchases_data, customers_data):
    result = map_purchases(customers_data, purchases_data, observer)

    expected = {1: [
        {'product_id': 101, 'price': 10.0, 'currency': 'dollars', 'quantity': 1, 'purchased_at': '2024-12-15'},
    ],
        2: [
            {'product_id': 201, 'price': 15.5, 'currency': 'dollars', 'quantity': 3, 'purchased_at': '2024-12-17'}
        ],
        3: [],
        4: []
    }
    assert result == expected


def test_core_map_purchases_errors(observer, purchases_data):
    empty_customers = pd.DataFrame()
    assert map_purchases(empty_customers, purchases_data, observer) is None


def test_core_create_bills(mapped_purchases, customers_data, observer):
    result = create_bills(customers_data, mapped_purchases, observer)
    expected = [{
                    'salutation': 'Female', 'last_name': 'LastTest','first_name': 'Test', 'email': 'test@test.com',
                    'purchases': [{'product_id': 101, 'price': 10.0, 'currency': 'dollars', 'quantity': 1,
                                   'purchased_at': '2024-12-15'}]
                },
                {
                    'salutation': 'Male', 'last_name': 'LastTest1','first_name': 'Test1', 'email': 'test1@test.com',
                    'purchases': [{'product_id': 201, 'price': 15.5, 'currency': 'dollars', 'quantity': 3,
                                   'purchased_at': '2024-12-17'}]
                }]

    assert result == expected

    assert "A customer 3 is missing some details, can't process their purchases" in observer.records[0]["message"]
    mapped_purchases[2] = []
    create_bills(customers_data, mapped_purchases, observer)
    assert "A customer 4 will be ignored because they don't have any purchases" in observer.records[1]["message"]


def test_core_send_bills(mocker, observer):
    mocker_response = mocker.MagicMock()
    mocker_response.ok = True
    mocker.patch("src.core.requests.put", return_value=mocker_response)
    assert send_bills([{"firstname": "test"}], "url", observer)


def test_core_send_bills_error(mocker, observer):
    response = send_bills([{"firstname": "test"}], "https://test.test", observer)
    assert response is False
    response = send_bills([{"firstname": "test"}], "", observer)
    assert response is False

