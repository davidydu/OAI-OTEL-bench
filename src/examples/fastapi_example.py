# /// script
# dependencies = ['logfire[fastapi,sqlite3,httpx]', 'fastapi', 'httpx', 'sqlite3']
# ///

"""A small FastAPI demo instrumented with Logfire."""

import os
import sqlite3
import httpx
import asyncio
import logfire
from fastapi import FastAPI

app = FastAPI()

logfire.configure(token=os.environ.get('LOGFIRE_TOKEN'))
logfire.instrument_fastapi(app, capture_headers=True)
logfire.instrument_sqlite3()

db_url = 'https://files.pydantic.run/pydantic_pypi.db'


async def main() -> None:
    with logfire.span('preparing database'):
        with logfire.span('downloading data'):
            r = httpx.get(db_url)
            r.raise_for_status()

        with logfire.span('create database'):
            with open('pydantic_pypi.db', 'wb') as f:
                f.write(r.content)
            connection = sqlite3.connect('pydantic_pypi.db')

    @app.get('/country/{country}/')
    async def read_item(country: str):
        cursor = connection.cursor()
        cursor.execute(
            'select count(*) from pydantic_pypi where country_code = ?',
            (country,),
        )
        row = cursor.fetchone()
        return {'count': row[0]}

    @app.post('/error/')
    async def error():
        raise RuntimeError('This is what an error looks like')

    t = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=t, base_url='http://test') as client:
        logfire.instrument_httpx(client, capture_headers=True)
        r = await client.get('/country/GB/')
        assert r.status_code == 200, r.status_code
        print('response:', r.json())

        try:
            await client.post('/error/')
        except RuntimeError as e:
            print('/error/ raised', e)


if __name__ == '__main__':
    asyncio.run(main())
