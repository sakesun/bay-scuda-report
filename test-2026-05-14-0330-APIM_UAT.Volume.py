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
    import os

    return mo, os


@app.cell(hide_code=True)
def _():
    from pathlib import Path
    data_dir = Path(__file__).resolve().parent / 'data'
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
    return f.startswith("2026-05-14T03.2") or f.startswith("2026-05-14T03.3")


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
def _(full_sources, mo, t):
    _df = mo.sql(
        f"""
        with t as (
          {full_sources}
        )
        select label, responseCode, responseMessage, count(*)
          from t where not success
          group by all
        """
    )
    return


if __name__ == "__main__":
    app.run()
