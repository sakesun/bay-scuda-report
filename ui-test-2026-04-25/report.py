# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    # import matplotlib.pyplot as plt
    # import seaborn as sns
    # from vega_datasets import data
    # import altair as alt
    # import numpy as np
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    _f = 'C:\\Users\\sakes\\projects\\xfer\\APIM_UAT.Normal\\20260420-150606-732.parquet'
    _df = mo.sql(
        f"""
        with t as (
          select label || ' / ' || string_split(URL, '/')[-1] as label
               , elapsed
               , responseCode
               , success
            from '{_f}'
        )
        pivot t
            on success in (true)
            using round(avg(elapsed)) as avg
                , min(elapsed) as min
                , max(elapsed) as max
                , quantile_cont(elapsed, 0.95) as p95
            group by label
        """
    )
    return


@app.cell
def _():
    from pathlib import Path
    data_dir = Path(__file__).resolve().parent / 'data'
    return (data_dir,)


@app.cell(hide_code=True)
def _():
    ALL_DATA = (
        ('172.19.10.87',  '2026-04-25T173141371747700.csv'),
        ('172.19.10.215', '2026-04-25T193927866133700.csv'),
        ('172.19.10.253', '2026-04-25T173323283190400.csv'),
        ('172.19.11.122', '2026-04-25T173623912440100.csv'),
        ('172.19.11.229', '2026-04-25T173700560122400.csv'),
        ('172.19.11.37',  '2026-04-25T173420067890900.csv'),
        ('172.19.11.50',  '2026-04-25T173524263773500.csv')
    )
    return (ALL_DATA,)


@app.cell(hide_code=True)
def _(data_dir):
    f1 = data_dir / '172.19.10.87/2026-04-25T173141371747700.csv'
    return


@app.cell(hide_code=True)
def _(data_dir):
    f2 = data_dir / '172.19.10.215/2026-04-25T193927866133700.csv'
    return


@app.cell(hide_code=True)
def _(ALL_DATA, data_dir):
    files = [data_dir / f'{ip}/{fname}' for (ip, fname) in ALL_DATA]
    sources = ' union all '.join(
        f"select label, elapsed, responseCode, success from '{f}'"
        for f in files
    )
    return (sources,)


@app.cell(hide_code=True)
def _(mo, sources):
    _df = mo.sql(
        f"""
        --

        with t as (
          {sources}
        )
        pivot t
            on success in (true)
            using min(elapsed) as min
                , round(avg(elapsed)) as avg
                , round(quantile_cont(elapsed, 0.95)) as p95
                , round(quantile_cont(elapsed, 0.96)) as p96
                , round(quantile_cont(elapsed, 0.97)) as p97
                , round(quantile_cont(elapsed, 0.98)) as p98
                , round(quantile_cont(elapsed, 0.99)) as p99
                , max(elapsed) as max
                , count(*) as cnt
            group by label
            order by label
        """
    )
    return


if __name__ == "__main__":
    app.run()
