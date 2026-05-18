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


@app.cell(hide_code=True)
def _():
    UIData = 'C:\\Users\\sakes\\projects\\xfer\\uitest\\2026-04-20T162622005655600.csv'
    return (UIData,)


@app.cell(hide_code=True)
def _(UIData, mo):
    _df = mo.sql(
        f"""
        -- 

        with t as (
          select label
               , elapsed
               , responseCode
               , success
            from '{UIData}'
        ) 
        pivot t 
            on success in (true)
            using round(avg(elapsed)) as avg
                , min(elapsed) as min
                , max(elapsed) as max
                , round(quantile_cont(elapsed, 0.95)) as p95
            group by label
            order by label
        """
    )
    return


if __name__ == "__main__":
    app.run()
