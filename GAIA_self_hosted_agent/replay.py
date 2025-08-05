import polars as pl
import json

DF = pl.read_parquet("GAIA_self_hosted_agent/logfire_sample_traces.parquet")
print(DF.select(pl.all().head(3)))
