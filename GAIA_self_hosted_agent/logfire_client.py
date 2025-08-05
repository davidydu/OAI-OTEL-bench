from io import StringIO
from logfire.query_client import AsyncLogfireQueryClient
import os
import polars as pl

async def main():
    trace_id = "01986299a5cc4d0485ea86845a381b33"
    query = f"""
            SELECT *
            FROM RECORDS
            WHERE trace_id = '{trace_id}'
              AND parent_span_id IS NOT NULL
            ORDER BY start_timestamp;
        """
    print(query)
    async with AsyncLogfireQueryClient(read_token=os.getenv('LOGFIRE_READ_TOKEN')) as client:
            # Load data as JSON, in column-oriented format
            # json_cols = await client.query_json(sql=query)
            # print(json_cols)

            # Load data as JSON, in row-oriented format
            json_rows = await client.query_json_rows(sql=query)
            print(json_rows)

            # Get read token info
            # read_token_info = await client.info()
            # print(read_token_info)

            # Retrieve data in arrow format, and load into a polars DataFrame
            # Note that JSON columns such as `attributes` will be returned as
            # JSON-serialized strings
            df_from_arrow = pl.from_arrow(await client.query_arrow(sql=query))
            # save the dataframe to Parquet
            df_from_arrow.write_parquet("GAIA_self_hosted_agent/logfire_sample_traces.parquet")
            # print(df_from_arrow)

            # Retrieve data in CSV format, and load into a polars DataFrame
            # Note that JSON columns such as `attributes` will be returned as
            # JSON-serialized strings
            df_from_csv = pl.read_csv(StringIO(await client.query_csv(sql=query)))
            df_from_csv.write_csv("GAIA_self_hosted_agent/logfire_sample_traces.csv")
            # print(df_from_csv)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
