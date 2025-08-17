import os
import polars as pl
from logfire.query_client import AsyncLogfireQueryClient

TRACE_LIST_CSV = "insights_extraction/validation_traces.csv"
OUT_PARQUET = "insights_extraction/validation_traces_full.parquet"


async def main():
    # 1) Read the provided CSV and get the first 165 unique trace_ids (in order)
    df_ids = pl.read_csv(TRACE_LIST_CSV)
    trace_ids = (
        df_ids.select(pl.col("trace_id"))
              .unique(maintain_order=True)
              .head(165)
              .to_series()
              .to_list()
    )

    # 2) Loop through these trace_ids and fetch their spans
    dfs = []
    async with AsyncLogfireQueryClient(read_token=os.getenv('LOGFIRE_READ_TOKEN')) as client:
        for trace_id in trace_ids:
            query = f"""
                SELECT *
                FROM RECORDS
                WHERE trace_id = '{trace_id}'
                ORDER BY start_timestamp;
            """
            print(f"Fetching trace_id={trace_id}")
            df = pl.from_arrow(await client.query_arrow(sql=query))
            dfs.append(df)

    # 3) Concatenate and write outputs
    df_all = pl.concat(dfs) if dfs else pl.DataFrame()
    os.makedirs(os.path.dirname(OUT_PARQUET), exist_ok=True)
    df_all.write_parquet(OUT_PARQUET)
    print(f"Wrote {OUT_PARQUET}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
