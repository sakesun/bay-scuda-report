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
    import altair as alt
    import numpy as np
    import os

    return alt, mo, os


@app.cell(hide_code=True)
def _():
    from pathlib import Path
    data_dir = Path(__file__).resolve().parent.parent / 'data'
    return (data_dir,)


@app.cell(hide_code=True)
def _(data_dir, os):
    def list_results(filter=lambda x: True):
        for machine in os.listdir(data_dir):
            for env in os.listdir(os.path.join(data_dir, machine)):
                for result in os.listdir(os.path.join(data_dir, machine, env)):
                    result_path = os.path.join(data_dir, machine, env, result)
                    if not os.path.isfile(result_path): continue
                    if filter and not filter(result): continue
                    yield result_path

    return (list_results,)


@app.cell
def _(data_dir, os):
    def list_errors_files(filter=lambda x: True):
        for machine in os.listdir(data_dir):
            for env in os.listdir(os.path.join(data_dir, machine)):
                for result in os.listdir(os.path.join(data_dir, machine, env)):
                    result_path = os.path.join(data_dir, machine, env, result)
                    if os.path.isfile(result_path): continue
                    if filter and not filter(result): continue
                    for error in os.listdir(os.path.join(data_dir, machine, env, result)):
                        error_path = os.path.join(data_dir, machine, env, result, error)
                        if not os.path.isfile(error_path): continue
                        yield (error, error_path)

    return (list_errors_files,)


@app.function
def result_filter(f):
    return f.startswith("2026-05-14T21.5") or f.startswith("2026-05-14T22.0")


@app.cell
def _(list_results):
    source_files = list(list_results(result_filter))
    return (source_files,)


@app.cell
def _(source_files):
    source_files
    return


@app.cell
def _(list_errors_files):
    len(list(list_errors_files(result_filter)))
    return


@app.cell
def _(source_files):
    sources = ' union all '.join(
        f"select label, elapsed, responseCode, success from '{f}'"
        for f in source_files
    )
    api_sources = f"select * from ({sources}) where label not like '%.%' and label not in ('NewBrowser', 'SignIn')"
    ui_sources  = f"select * from ({sources}) where label     like '%.%' or  label     in ('NewBrowser', 'SignIn')"
    full_sources = ' union all '.join(
        f"select * from '{f}'"
        for f in source_files
    )
    return api_sources, full_sources, ui_sources


@app.cell
def _(api_sources, mo):
    _df = mo.sql(
        f"""
        --

        with t as (
        {api_sources}
        )
        pivot t
            on success in (true)
            using min(elapsed) as min
                , round(avg(elapsed)) as avg
                , round(quantile_cont(elapsed, 0.90)) as p90
                , round(quantile_cont(elapsed, 0.95)) as p95
                , round(quantile_cont(elapsed, 0.98)) as p98
                , round(quantile_cont(elapsed, 0.99)) as p99
                , max(elapsed) as max
                , count(*) as cnt
            group by label
            order by label
        """
    )
    return


@app.cell(hide_code=True)
def _(mo, ui_sources):
    _df = mo.sql(
        f"""
        --

        with t as (
        {ui_sources}
        )
        pivot t
            on success in (true)
            using min(elapsed) as min
                , round(avg(elapsed)) as avg
                , round(quantile_cont(elapsed, 0.90)) as p90
                , round(quantile_cont(elapsed, 0.95)) as p95
                , round(quantile_cont(elapsed, 0.98)) as p98
                , round(quantile_cont(elapsed, 0.99)) as p99
                , max(elapsed) as max
                , count(*) as cnt
            group by label
            order by label
        """
    )
    return


@app.cell
def _(api_sources, mo, t):
    _df = mo.sql(
        f"""
        with t as (
          {api_sources}
        )
        select label
             , count(*) as cnt
             , count(nullif(success, True)) as err
             , (case when err = 0 then null else round(err/cnt*100, 2) end) as "%err"
          from t 
          group by label
          having "%err" > 0
          order by 4 desc
        """
    )
    return


@app.cell
def _(api_sources, mo, t):
    _df = mo.sql(
        f"""
        with t as (
          {api_sources}
        )
        select count(*) as cnt
             , count(nullif(success, True)) as err
             , (case when err = 0 then null else round(err/cnt*100, 2) end) as "%err"
          from t 
          group by all
          order by 1
        """
    )
    return


@app.cell
def _(full_sources, mo, t):
    _df = mo.sql(
        f"""
        with t as (
          {full_sources}
        )
        select failureMessage as failureMessage
             , label, count(*) from t where not success
          group by all
          order by count(*) desc
        """
    )
    return


@app.cell
def _(api_sources, mo, t):
    _df = mo.sql(
        f"""
        with t as (
          {api_sources}
        )
        select label, responseCode, responseMessage, count(*)
          from t where not success
          group by all
        """
    )
    return


@app.cell
def _(full_sources, mo, t):
    toplot = mo.sql(
        f"""
        with t as (
          {full_sources}
        )
        select to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok' as timeStamp
             , elapsed
             , label
             , success
          from t
        """
    )
    return (toplot,)


@app.cell
def _(alt, mo, toplot):
    chart = alt.Chart(toplot).mark_line().encode(
        x='timeStamp:T',
        y='elapsed:Q'
    ).properties(width='container').interactive() # Allows panning/zooming

    time_plot = mo.ui.altair_chart(chart)
    time_plot
    return


@app.cell
def _():
    select_percentiles = [
        f"(select round(quantile_cont(elapsed, {_i} / 100)) from S)  as '{_i}'"
        for _i in range(0, 101)
    ]
    select_percentiles_columns = [*[f'{_i}' for _i in range(0, 101)]]
    return select_percentiles, select_percentiles_columns


@app.cell
def _(api_sources, mo, select_percentiles, select_percentiles_columns):
    percentiles = mo.sql(
        f"""
        with 
          S as (select elapsed from ({api_sources})),
          R as (select {','.join(select_percentiles)}),
          U as (
            UNPIVOT R ON {','.join(select_percentiles_columns)}
            INTO NAME P VALUE elapsed)
          select P::numeric as P, elapsed from U where P <> '100'
    
        """,
        output=False
    )
    return (percentiles,)


@app.cell
def _(alt, mo, percentiles):
    pchart = alt.Chart(percentiles).mark_line().encode(
        x='P:T',
        y='elapsed:Q'
    ).properties(width='container').interactive() # Allows panning/zooming

    ptime_plot = mo.ui.altair_chart(pchart)
    ptime_plot
    return


if __name__ == "__main__":
    app.run()
