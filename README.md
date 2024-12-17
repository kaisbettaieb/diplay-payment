# In-Flight Payment Processing CLI

The project is a command line interface to process customer and purchase data from CSV files 
and send the formatted data to a Display purchase processing API endpoint.

## Setup

1. Clone the Repository

2. Create a virtual environment
```bash
python -m venv venv
```

3. Activate the virtual environment
```bash
venv/Scripts/activate
```

4. Install Dependencies
```bash
pip install -r requirements.txt
```
4.b Install Dependencies for tests
```bash
pip install -r requirements-test.txt
```

## Usage

```bash
python main.py customers.csv purchases.csv --url https://myhostname.com/v1/customers
```

### Required Arguments
1. Path to the customers CSV file.
2. Path to the purchase CSV file.

### Optional Parameters
1. `--url`: The Display payment processing Endpoint.

*PS: if the parameter `--url` is not provided it will default to the environement variable* `API_URL` 


## Potential Improvements and Features

* Better files validation: validate customers.csv and purchases.csv schema and missing data

* Api retry: Verify failed api requests and implement safeguards such as wait and retry .

* Better error handling: improve critial errors handling such as when customers details are missing crucial information

* Alert system: improve The observer by adding alerting system in case of critial errors

* Unit Tests: Add more unitests for edge cases of main cli function
