from io import StringIO
from logfire.query_client import AsyncLogfireQueryClient
import os
import polars as pl

async def main():
    N = 165
    # Exclude httpx-instrumented root spans via otel_scope_name
    query = f"""
            SELECT *
            FROM RECORDS
            WHERE COALESCE(LOWER(otel_scope_name), '') NOT LIKE '%httpx%'
                AND parent_span_id IS NULL
            ORDER BY start_timestamp DESC
            LIMIT {N}
        """
    
    print(query)

    async with AsyncLogfireQueryClient(read_token=os.getenv("LOGFIRE_READ_TOKEN")) as client:
        # Arrow -> Polars -> Parquet
        df_from_arrow = pl.from_arrow(await client.query_arrow(sql=query))
        df_from_arrow.write_parquet("insights_extraction/validation_traces.parquet")

        # CSV -> Polars -> CSV file
        df_from_csv = pl.read_csv(StringIO(await client.query_csv(sql=query)))
        df_from_csv.write_csv("insights_extraction/validation_traces.csv")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
