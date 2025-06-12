# /// script
# dependencies = ['logfire[fastapi,sqlite3,httpx]', 'fastapi', 'httpx', 'sqlite3']
# ///

# This example demonstrates a simple FastAPI app with sqlite database.

import sqlite3

import logfire
import httpx
from fastapi import FastAPI

# create a fastapi app, see https://fastapi.tiangolo.com/reference/fastapi/
app = FastAPI()

# configure logfire
logfire.configure(token='pylf_v1_us_9bZ57RDYs2P0LbbxcjK95kxZKL0jqFDhKqjYtTR7Wwy7')
logfire.instrument_fastapi(app, capture_headers=True)
logfire.instrument_sqlite3()

# sqlite database URL
db_url = 'https://files.pydantic.run/pydantic_pypi.db'

# download the data and create the database
with logfire.span('preparing database'):
    with logfire.span('downloading data'):
        r = httpx.get(db_url)
        r.raise_for_status()

    with logfire.span('create database'):
        with open('pydantic_pypi.db', 'wb') as f:
            f.write(r.content)
        connection = sqlite3.connect('pydantic_pypi.db')


# create an endpoint for getting the number of power plants in a country
@app.get('/country/{country}/')
async def read_item(country: str):
    cursor = connection.cursor()
    cursor.execute(
        'select count(*) from pydantic_pypi where country_code = ?',
        (country,)
    )
    row = cursor.fetchone()
    return {'count': row[0]}


# this endpoint just raise an exception, so you can see how errors
# are displayed in Logfire
@app.post('/error/')
async def error():
    raise RuntimeError('This is what an error looks like')



# to make requests to the fastapi appl, we use a custom transport
# with httpx, see https://www.python-httpx.org/advanced/transports/
t = httpx.ASGITransport(app=app)
async with httpx.AsyncClient(transport=t, base_url='http://test') as client:
    logfire.instrument_httpx(client, capture_headers=True)
    # make a request to the country endpoint
    r = await client.get('/country/GB/')
    assert r.status_code == 200, r.status_code
    print('response:', r.json())

    try:
        r = await client.post('/error/')
    except RuntimeError as e:
        print('/error/ raised', e)

