# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np
    import os
    from pathlib import Path
    from datetime import datetime, timedelta

    return Path, alt, datetime, mo, timedelta


@app.cell(hide_code=True)
def _(Path):
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
    assert data_dir.exists()
    return (data_dir,)


@app.cell(hide_code=True)
def _(data_dir):
    def list_result_files(filter=lambda x: True):
        return [f 
            for machine in data_dir.iterdir() if machine.is_dir()
            for env in machine.iterdir() if env.is_dir()
            for f in env.iterdir() if f.is_file() and (filter is None or filter(f.name))]

    return (list_result_files,)


@app.cell(hide_code=True)
def _(data_dir):
    def list_errors_files(filter=lambda x: True):
        return [error_file 
            for machine in data_dir.iterdir() if machine.is_dir()
            for env in machine.iterdir() if env.is_dir()
            for error_dir in env.iterdir() if error_dir.is_dir() and (filter is None or filter(error_dir.name))
            for error_file in error_dir.iterdir() if error_file.is_file()]

    return (list_errors_files,)


@app.cell
def _(datetime, timedelta):
    def _prefix(dt): return dt.isoformat().replace(':', '.')[:len('YYYY-MM-DDTHH.MM')]
    def filter_for(yyyy, mm, dd, hh, nn):
        dt = datetime(yyyy, mm, dd, hh, nn)
        m1 = timedelta(minutes=1)
        m2 = timedelta(minutes=2)
        allowed_datetimes = [dt, dt - m1, dt - m2, dt + m1, dt + m2]
        allowed_prefixes = [_prefix(dt) for dt in allowed_datetimes]
        def f(name): return name.startswith(tuple(allowed_prefixes))
        return f
    def filter_for_range(start, end):
        m2 = timedelta(minutes=2)
        dt1 = datetime(*start) - m2
        dt2 = datetime(*end) + m2
        def f(name): return (_prefix(dt1) <= name <= _prefix(dt2))
        return f
    def merge_filters(*filters):
        def f(name):
            return any(ff(name) for ff in filters)
        return f

    return filter_for, merge_filters


@app.cell
def _(filter_for, list_errors_files, list_result_files, merge_filters):
    scope = merge_filters(
        filter_for(2026, 5, 16,  5, 30),
        filter_for(2026, 5, 16,  6, 46),
        filter_for(2026, 5, 16, 15, 57),
        filter_for(2026, 5, 16, 17, 13),
        filter_for(2026, 5, 16, 18, 29),
        filter_for(2026, 5, 16, 19, 45))
    result_files = list_result_files(scope)
    error_files = list_errors_files(scope)
    return (result_files,)


@app.cell
def _(result_files):
    result_files
    return


@app.cell
def _(result_files):
    sources = ' union all '.join(
        f"select label, elapsed, responseCode, success from '{f}'"
        for f in result_files
    )
    api_sources = f"select * from ({sources}) where label not like '%.%' and label not in ('NewBrowser', 'SignIn')"
    ui_sources  = f"select * from ({sources}) where label     like '%.%' or  label     in ('NewBrowser', 'SignIn')"
    full_sources = ' union all '.join(
        f"select * from '{f}'"
        for f in result_files
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
        from t where not success
        """,
        output=False
    )
    return (toplot,)


@app.cell
def _(alt, mo, toplot):
    chart = alt.Chart(toplot).mark_line().encode(
        x='timeStamp:T',
        y='elapsed:Q',
        color='label:N'    
    ).properties(width='container').interactive() # Allows panning/zooming

    time_plot = mo.ui.altair_chart(chart)
    time_plot
    return


@app.cell
def _(api_sources, mo, s):
    _df = mo.sql(
        f"""
        with 
          S as ({api_sources})
          select 
              (select round(quantile_cont(elapsed, 1 / 100)) from S) P01,
              (select round(quantile_cont(elapsed, 1 / 100)) from S) P99,
              (select count(*) from S)
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
        select threadName
             , to_timestamp(t.timeStamp/1000) AT TIME ZONE 'Asia/Bangkok' as timeStamp
             , elapsed
             , label
             , success
          from t
         where elapsed::numeric > 5000
           and (label like '%.%' or label in ('NewBrowser', 'SignIn'))
        """
    )
    return


if __name__ == "__main__":
    app.run()
