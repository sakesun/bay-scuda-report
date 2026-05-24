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
    from great_tables import GT

    return GT, Path, alt, datetime, mo, pd, timedelta


@app.cell
def _(Path):
    def get_data_dir():
        d = Path(__file__).resolve()
        while not (d / 'data').exists():
            parent = d.parent
            if parent == d: raise Exception("data path could not be found")
            d = parent
        return d / 'data'

    return (get_data_dir,)


@app.cell
def _(GT, get_data_dir, pd):
    data_dir = get_data_dir()
    assert data_dir.exists()

    def list_result_files(filter=lambda x: True):
        return [f.relative_to(data_dir) 
            for machine in data_dir.iterdir() if machine.is_dir()
            for env in machine.iterdir() if env.is_dir()
            for f in env.iterdir() if f.is_file() and (filter is None or filter(f.name))]

    def list_errors_files(filter=lambda x: True):
        return [error_file.relative_to(data_dir)
            for machine in data_dir.iterdir() if machine.is_dir()
            for env in machine.iterdir() if env.is_dir()
            for error_dir in env.iterdir() if error_dir.is_dir() and (filter is None or filter(error_dir.name))
            for error_file in error_dir.iterdir() if error_file.is_file()]

    def files_table(files, *, tab_header=None):
        filenames = [f for f in files]
        r = GT(pd.DataFrame(files, columns=['File Name']))
        if tab_header:
            if isinstance(tab_header, str): r = r.tab_header(tab_header)
            if isinstance(tab_header, dict): r = r.tab_header(**tab_header)
        r = r.cols_align('left')
        r = r.opt_vertical_padding(scale=0)
        return r

    return data_dir, files_table, list_errors_files, list_result_files


@app.cell
def _(data_dir, datetime, mo, timedelta):
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
    def sql_unions(files, *, select='*', where=None):
        if isinstance(select, list): select = ', '.join(select)
        where_option = f' where {where}' if where else ''
        return '\n union all \n'.join(
            f"select {select} from '{data_dir / f}'" + where_option
            for f in files)
    def with_raw_src_from_files(files, sql, /, *, select='*', where=None):
        unions = sql_unions(files, select=select, where=where)
        return f"with src as (\n{unions}\n) {sql}"
    def with_src_from_files(files, sql, /, *, select='*', where=None):
        unions = sql_unions(files, select=select, where=where)
        return f"""
            with src as (
                select 
                    to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok' as timeStamp
                  , elapsed
                  , label
                  , success
                  , responseCode
                  , failureMessage
                from (
                {unions}
                )
            ) 
            {sql}
        """
    def count_records_in_files(files, where=None):
        return mo.sql(with_src_from_files(files, 'select count(*) from src', where=where))
    def get_result_rows(files, where=None):
        return mo.sql(with_src_from_files(files, 'select * from src', where=where))

    IS_API = "(label not like '%.%' and label not in ('NewBrowser', 'SignIn'))"
    IS_UI  = "(label     like '%.%' or  label     in ('NewBrowser', 'SignIn'))"

    return IS_API, filter_for, get_result_rows, with_src_from_files


@app.cell
def _(filter_for, list_errors_files, list_result_files):
    scope = filter_for(2026, 5, 22, 21, 00)
    result_files = list_result_files(scope)
    error_files = list_errors_files(scope)
    return error_files, result_files


@app.cell
def _(IS_API, mo, result_files, with_src_from_files):
    mo.sql(with_src_from_files(result_files, 'select * from src limit 10', where=IS_API))
    return


@app.cell
def _(error_files, files_table, mo, result_files):
    mo.hstack([
      files_table(result_files, tab_header=dict(title='Result Files', subtitle=f'({len(result_files)} files)')),
      f'{len(error_files)} error files'
    ])
    return


@app.cell
def _(IS_API, result_files, with_src_from_files):
    print(repr(with_src_from_files(result_files, """
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
    """, where=IS_API)))
    return


@app.cell
def _(IS_API, mo, result_files, with_src_from_files):
    mo.sql(with_src_from_files(result_files, """
        pivot src
            on success in (true)
            using min(elapsed) as min
                , round(avg(elapsed)) as avg
                , round(quantile_cont(elapsed, 0.95)) as p95
                , round(quantile_cont(elapsed, 0.98)) as p98
                , round(quantile_cont(elapsed, 0.99)) as p99
                , max(elapsed) as max
                , count(*) as cnt
            group by label
            order by label
    """, where=IS_API))
    return


@app.cell
def _(IS_API, mo, result_files, with_src_from_files):
    mo.sql(with_src_from_files(result_files, """
        select label
             , count(*) as cnt
             , count(nullif(success, True)) as err
             , (case when err = 0 then null else round(err/cnt*100, 2) end) as "%err"
          from src
          group by label
          having "err" > 0
          order by 4 desc
    """, where=IS_API))
    return


@app.cell
def _(IS_API, alt, get_result_rows, mo, result_files):
    chart = alt.Chart(get_result_rows(result_files, IS_API)).mark_point().encode(
        x='timeStamp:T',
        y='elapsed:Q',
        color='label:N'    
    ).properties(width='container').interactive() # Allows panning/zooming

    time_plot = mo.ui.altair_chart(chart)
    time_plot
    return


if __name__ == "__main__":
    app.run()
