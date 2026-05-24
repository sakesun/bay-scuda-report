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
    return IS_API, IS_UI, filter_for, with_src_from_files


@app.cell
def _(
    IS_API,
    IS_UI,
    alt,
    files_table,
    list_errors_files,
    list_result_files,
    mo,
    with_src_from_files,
):
    class WorkSet:
        def __init__(self, scope, where=None):
            self.scope = scope
            self.result_files = list_result_files(scope)
            self.error_files = list_errors_files(scope)
            self.where = where
        @property
        def api(self): return WorkSet(self.scope, IS_API)
        @property
        def ui(self): return WorkSet(self.scope, IS_UI)
        def show_sources(self):
            return mo.hstack([
                files_table(self.result_files, tab_header=dict(title='Result Files', subtitle=f'({len(self.result_files)} files)')),
                f'{len(self.error_files)} error files'
            ])
        def query(self, sql):
            return mo.sql(with_src_from_files(self.result_files, sql, where=self.where))
        def response_times(self):
            return self.query("""
                pivot src
                    using min(elapsed) as min
                        , round(avg(elapsed)) as avg
                        , round(quantile_cont(elapsed, 0.90)) as p90
                        , round(quantile_cont(elapsed, 0.95)) as p95
                        , round(quantile_cont(elapsed, 0.99)) as p99
                        , max(elapsed) as max
                        , count(*) as cnt
                    group by label
                    order by label""")
        def error_rates(self):
            return self.query("""
                select label
                     , count(*) as cnt
                     , count(nullif(success, True)) as err
                     , (case when err = 0 then null else round(err/cnt*100, 2) end) as "%err"
                  from src
                  group by label
                  having "%err" > 0
                  order by 4 desc""")
        def failures(self):
            return self.query("""
                select responseCode
                     , failureMessage as failureMessage
                     , label, count(*) 
                  from src 
                  where not success
                  group by all
                  order by count(*) desc""")
        def timeline_response_times(self):
            data = self.query("""
                select date_trunc('second', timeStamp) as timeStamp
                     , label
                     , success
                     , max(elapsed) as elapsed
                  from src
                  group by all""")
            chart = alt.Chart(data).mark_point().encode(
                x='timeStamp:T',
                y='elapsed:Q',
                color='label:N'    
            ).properties(width='container').interactive()
            return mo.ui.altair_chart(chart)
        def timeline_error_response_times(self):
            data = self.query("""
                select timeStamp
                     , label
                     , success
                     , elapsed
                  from src
                  where not success""")
            chart = alt.Chart(data).mark_point().encode(
                x='timeStamp:T',
                y='elapsed:Q',
                color='label:N'    
            ).properties(width='container').interactive()
            return mo.ui.altair_chart(chart)
        def timeline_tps(self):
            data = self.query("""
                select date_trunc('second', timeStamp) as timeStamp
                     , label
                     , count(*) as count
                  from src
                  group by all""")
            chart = alt.Chart(data).mark_point().encode(
                x='timeStamp:T',
                y='count:Q',
                color='label:N'
            ).properties(width='container').interactive()
            return mo.ui.altair_chart(chart)
        def timeline_error_rates(self):
            data = self.query("""
                select date_trunc('second', timeStamp) as timeStamp
                     , label
                     , count(*) as count
                  from src
                  where not success
                  group by all""")
            chart = alt.Chart(data).mark_point().encode(
                x='timeStamp:T',
                y='count:Q',
                color='label:N'
            ).properties(width='container').interactive()
            return mo.ui.altair_chart(chart)
        def percentiles(self):
            select_percentiles = [
                f"(select round(quantile_cont(elapsed, {_i} / 100)) from S)  as '{_i}'"
                for _i in range(0, 101)]
            select_percentiles_columns = [*[f'{_i}' for _i in range(0, 101)]]
            data = self. query(f"""
                ,
                S as (select elapsed from src where label='CreateIndividual'),
                R as (select {','.join(select_percentiles)}),
                U as (
                    UNPIVOT R ON {','.join(select_percentiles_columns)}
                    INTO NAME P VALUE elapsed)
                select P::numeric as P, elapsed from U where P <> '100'
            """)
            data2 = self. query(f"""
                ,
                S as (select elapsed from src where label='SearchIndividual'),
                R as (select {','.join(select_percentiles)}),
                U as (
                    UNPIVOT R ON {','.join(select_percentiles_columns)}
                    INTO NAME P VALUE elapsed)
                select P::numeric as P, elapsed from U where P <> '100'
            """)
            pchart = alt.Chart(data).mark_line().encode(
                x='P:T',
                y='elapsed:Q',
                color=alt.value('red')
            )
            pchart2 = alt.Chart(data2).mark_line().encode(
                x='P:T',
                y='elapsed:Q',
                color=alt.value('blue')
            )        
            # pchart = alt.Chart(data).mark_line().encode(
            #     x='P:T',
            #     y='elapsed:Q'
            # ).properties(width='container').interactive()
            layered_chart = alt.layer(pchart, pchart2)
            return mo.ui.altair_chart(layered_chart)
            #return mo.ui.altair_chart(pchart)
        def percentiles_sql(self):
            select_percentiles = [
                f"(select round(quantile_cont(elapsed, {_i} / 100)) from S)  as '{_i}'"
                for _i in range(0, 101)]
            select_percentiles_columns = [*[f'{_i}' for _i in range(0, 101)]]
            data = with_src_from_files(self.result_files, f"""
                ,
                S as (select elapsed from src where label='CreateIndividual'),
                R as (select {','.join(select_percentiles)}),
                U as (
                    UNPIVOT R ON {','.join(select_percentiles_columns)}
                    INTO NAME P VALUE elapsed)
                select P::numeric as P, elapsed from U where P <> '100'
            """)
            return data
        

    return (WorkSet,)


@app.cell
def _(ws):
    ws.api.percentiles()
    return


@app.cell(hide_code=True)
def _(ws):
    print(ws.percentiles_sql())
    return


@app.cell(hide_code=True)
def _(mo, r, s, src, u):
    _df = mo.sql(
        f"""
        with sss as (


                with src as (
                    select 
                        to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok' as timeStamp
                      , elapsed
                      , label
                      , success
                      , responseCode
                      , failureMessage
                    from (
                    select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2577\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2578\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2579\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2580\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2581\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2582\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2583\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2584\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2585\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2587\\UAT.Volume\\2026-05-19T21.00.03.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2588\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2589\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2590\\UAT.Volume\\2026-05-19T21.00.00.parquet'
         union all 
        select * from 'C:\\Users\\sakes\\projects\\bay-scuda-report\\data\\D5000N2591\\UAT.Volume\\2026-05-19T21.00.00.parquet'
                    )
                ) 
        
                    ,
                    S as (select elapsed from src where label='CreateIndividual'),
                    R as (select (select round(quantile_cont(elapsed, 0 / 100)) from S)  as '0',(select round(quantile_cont(elapsed, 1 / 100)) from S)  as '1',(select round(quantile_cont(elapsed, 2 / 100)) from S)  as '2',(select round(quantile_cont(elapsed, 3 / 100)) from S)  as '3',(select round(quantile_cont(elapsed, 4 / 100)) from S)  as '4',(select round(quantile_cont(elapsed, 5 / 100)) from S)  as '5',(select round(quantile_cont(elapsed, 6 / 100)) from S)  as '6',(select round(quantile_cont(elapsed, 7 / 100)) from S)  as '7',(select round(quantile_cont(elapsed, 8 / 100)) from S)  as '8',(select round(quantile_cont(elapsed, 9 / 100)) from S)  as '9',(select round(quantile_cont(elapsed, 10 / 100)) from S)  as '10',(select round(quantile_cont(elapsed, 11 / 100)) from S)  as '11',(select round(quantile_cont(elapsed, 12 / 100)) from S)  as '12',(select round(quantile_cont(elapsed, 13 / 100)) from S)  as '13',(select round(quantile_cont(elapsed, 14 / 100)) from S)  as '14',(select round(quantile_cont(elapsed, 15 / 100)) from S)  as '15',(select round(quantile_cont(elapsed, 16 / 100)) from S)  as '16',(select round(quantile_cont(elapsed, 17 / 100)) from S)  as '17',(select round(quantile_cont(elapsed, 18 / 100)) from S)  as '18',(select round(quantile_cont(elapsed, 19 / 100)) from S)  as '19',(select round(quantile_cont(elapsed, 20 / 100)) from S)  as '20',(select round(quantile_cont(elapsed, 21 / 100)) from S)  as '21',(select round(quantile_cont(elapsed, 22 / 100)) from S)  as '22',(select round(quantile_cont(elapsed, 23 / 100)) from S)  as '23',(select round(quantile_cont(elapsed, 24 / 100)) from S)  as '24',(select round(quantile_cont(elapsed, 25 / 100)) from S)  as '25',(select round(quantile_cont(elapsed, 26 / 100)) from S)  as '26',(select round(quantile_cont(elapsed, 27 / 100)) from S)  as '27',(select round(quantile_cont(elapsed, 28 / 100)) from S)  as '28',(select round(quantile_cont(elapsed, 29 / 100)) from S)  as '29',(select round(quantile_cont(elapsed, 30 / 100)) from S)  as '30',(select round(quantile_cont(elapsed, 31 / 100)) from S)  as '31',(select round(quantile_cont(elapsed, 32 / 100)) from S)  as '32',(select round(quantile_cont(elapsed, 33 / 100)) from S)  as '33',(select round(quantile_cont(elapsed, 34 / 100)) from S)  as '34',(select round(quantile_cont(elapsed, 35 / 100)) from S)  as '35',(select round(quantile_cont(elapsed, 36 / 100)) from S)  as '36',(select round(quantile_cont(elapsed, 37 / 100)) from S)  as '37',(select round(quantile_cont(elapsed, 38 / 100)) from S)  as '38',(select round(quantile_cont(elapsed, 39 / 100)) from S)  as '39',(select round(quantile_cont(elapsed, 40 / 100)) from S)  as '40',(select round(quantile_cont(elapsed, 41 / 100)) from S)  as '41',(select round(quantile_cont(elapsed, 42 / 100)) from S)  as '42',(select round(quantile_cont(elapsed, 43 / 100)) from S)  as '43',(select round(quantile_cont(elapsed, 44 / 100)) from S)  as '44',(select round(quantile_cont(elapsed, 45 / 100)) from S)  as '45',(select round(quantile_cont(elapsed, 46 / 100)) from S)  as '46',(select round(quantile_cont(elapsed, 47 / 100)) from S)  as '47',(select round(quantile_cont(elapsed, 48 / 100)) from S)  as '48',(select round(quantile_cont(elapsed, 49 / 100)) from S)  as '49',(select round(quantile_cont(elapsed, 50 / 100)) from S)  as '50',(select round(quantile_cont(elapsed, 51 / 100)) from S)  as '51',(select round(quantile_cont(elapsed, 52 / 100)) from S)  as '52',(select round(quantile_cont(elapsed, 53 / 100)) from S)  as '53',(select round(quantile_cont(elapsed, 54 / 100)) from S)  as '54',(select round(quantile_cont(elapsed, 55 / 100)) from S)  as '55',(select round(quantile_cont(elapsed, 56 / 100)) from S)  as '56',(select round(quantile_cont(elapsed, 57 / 100)) from S)  as '57',(select round(quantile_cont(elapsed, 58 / 100)) from S)  as '58',(select round(quantile_cont(elapsed, 59 / 100)) from S)  as '59',(select round(quantile_cont(elapsed, 60 / 100)) from S)  as '60',(select round(quantile_cont(elapsed, 61 / 100)) from S)  as '61',(select round(quantile_cont(elapsed, 62 / 100)) from S)  as '62',(select round(quantile_cont(elapsed, 63 / 100)) from S)  as '63',(select round(quantile_cont(elapsed, 64 / 100)) from S)  as '64',(select round(quantile_cont(elapsed, 65 / 100)) from S)  as '65',(select round(quantile_cont(elapsed, 66 / 100)) from S)  as '66',(select round(quantile_cont(elapsed, 67 / 100)) from S)  as '67',(select round(quantile_cont(elapsed, 68 / 100)) from S)  as '68',(select round(quantile_cont(elapsed, 69 / 100)) from S)  as '69',(select round(quantile_cont(elapsed, 70 / 100)) from S)  as '70',(select round(quantile_cont(elapsed, 71 / 100)) from S)  as '71',(select round(quantile_cont(elapsed, 72 / 100)) from S)  as '72',(select round(quantile_cont(elapsed, 73 / 100)) from S)  as '73',(select round(quantile_cont(elapsed, 74 / 100)) from S)  as '74',(select round(quantile_cont(elapsed, 75 / 100)) from S)  as '75',(select round(quantile_cont(elapsed, 76 / 100)) from S)  as '76',(select round(quantile_cont(elapsed, 77 / 100)) from S)  as '77',(select round(quantile_cont(elapsed, 78 / 100)) from S)  as '78',(select round(quantile_cont(elapsed, 79 / 100)) from S)  as '79',(select round(quantile_cont(elapsed, 80 / 100)) from S)  as '80',(select round(quantile_cont(elapsed, 81 / 100)) from S)  as '81',(select round(quantile_cont(elapsed, 82 / 100)) from S)  as '82',(select round(quantile_cont(elapsed, 83 / 100)) from S)  as '83',(select round(quantile_cont(elapsed, 84 / 100)) from S)  as '84',(select round(quantile_cont(elapsed, 85 / 100)) from S)  as '85',(select round(quantile_cont(elapsed, 86 / 100)) from S)  as '86',(select round(quantile_cont(elapsed, 87 / 100)) from S)  as '87',(select round(quantile_cont(elapsed, 88 / 100)) from S)  as '88',(select round(quantile_cont(elapsed, 89 / 100)) from S)  as '89',(select round(quantile_cont(elapsed, 90 / 100)) from S)  as '90',(select round(quantile_cont(elapsed, 91 / 100)) from S)  as '91',(select round(quantile_cont(elapsed, 92 / 100)) from S)  as '92',(select round(quantile_cont(elapsed, 93 / 100)) from S)  as '93',(select round(quantile_cont(elapsed, 94 / 100)) from S)  as '94',(select round(quantile_cont(elapsed, 95 / 100)) from S)  as '95',(select round(quantile_cont(elapsed, 96 / 100)) from S)  as '96',(select round(quantile_cont(elapsed, 97 / 100)) from S)  as '97',(select round(quantile_cont(elapsed, 98 / 100)) from S)  as '98',(select round(quantile_cont(elapsed, 99 / 100)) from S)  as '99',(select round(quantile_cont(elapsed, 100 / 100)) from S)  as '100'),
                    U as (
                        UNPIVOT R ON 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100
                        INTO NAME P VALUE elapsed)
                    select P::numeric as P, elapsed from U where P <> '100'

        )
        select * from sss s1 join sss s2 on s1.P = s2.P
        """
    )
    return


@app.cell
def _(WorkSet, filter_for):
    ws = WorkSet(filter_for(2026, 5, 19, 21, 00))
    return (ws,)


@app.cell
def _(ws):
    ws.show_sources()
    return


@app.cell
def _(ws):
    ws.api.response_times()
    return


@app.cell
def _(ws):
    ws.api.error_rates()
    return


@app.cell
def _(ws):
    ws.ui.error_rates()
    return


@app.cell
def _(ws):
    ws.api.failures()
    return


@app.cell
def _(ws):
    ws.ui.failures()
    return


@app.cell
def _(ws):
    toplot = ws.query("""
        select date_trunc('second', timeStamp) as timeStamp
             , label
             , success
             , max(elapsed) as elapsed
          from src
          group by all""")
    toplot
    return


@app.cell
def _(ws):
    toploterr = ws.query("""
        select timeStamp
             , label
             , success
             , elapsed
          from src
          where not success""")
    toploterr
    return


@app.cell
def _(ws):
    ws.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.timeline_error_response_times()
    return


@app.cell
def _(ws):
    ws.api.timeline_tps()
    return


@app.cell
def _(ws):
    ws.ui.timeline_tps()
    return


@app.cell
def _(ws):
    ws.timeline_error_rates()
    return


if __name__ == "__main__":
    app.run()
