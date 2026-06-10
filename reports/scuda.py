from functools import cached_property
import marimo as mo
import pandas as pd
import altair as alt
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta
from great_tables import GT

def get_data_dir():
    d = Path(__file__).resolve()
    while not (d / 'data').exists():
        parent = d.parent
        if parent == d: raise Exception("data path could not be found")
        d = parent
    return d / 'data'

data_dir = get_data_dir()
assert data_dir.exists()

HIDDEN_LABELS = ['Get Token', 'SignIn', 'NewBrowser']

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
    d = pd.DataFrame(files, columns=['File Name'])
    # d['size'] = d['File Name'].apply(lambda v: (data_dir / v).stat().st_size)
    r = GT(d)
    if tab_header:
        if isinstance(tab_header, str): r = r.tab_header(tab_header)
        if isinstance(tab_header, dict): r = r.tab_header(**tab_header)
    r = r.cols_align('left')
    # r = r.cols_align(align="right", columns=["size"])
    # r = r.fmt_number(columns="size", decimals=0)
    r = r.tab_options(table_body_vlines_style='solid')
    r = r.opt_vertical_padding(scale=0)
    return r

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

class WorkSet:
    def __init__(self, scope, where=None):
        self.scope = scope
        self.result_files = list_result_files(scope)
        self.error_files = list_errors_files(scope)
        self.where = where
    def get_api(self, where): return WorkSet(self.scope, f"({IS_API}) and ({where})")
    def get_ui(self, where): return WorkSet(self.scope, f"({IS_UI}) and ({where})")
    @cached_property
    def api(self): return self.get_api(f"label not in ({",".join(f"'{s}'" for s in HIDDEN_LABELS)})")
    @cached_property
    def ui(self): return self.get_ui(f"success and label not in ({",".join(f"'{s}'" for s in HIDDEN_LABELS)})")
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
        ).properties(width='container')
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
        ).properties(width='container')
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
        ).properties(width='container')
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
        ).properties(width='container')
        return mo.ui.altair_chart(chart)
    def percentiles_sql(self, label=None):
        select_percentiles = [
            f"(select round(quantile_cont(elapsed, {_i} / 100)) from S)  as '{_i}'"
            for _i in range(0, 101)]
        select_percentiles_columns = [*[f'{_i}' for _i in range(0, 101)]]
        data = with_src_from_files(self.result_files, f"""
            ,
            S as (select elapsed from src {("where label='" + label + "'") if label else ''}),
            R as (select {','.join(select_percentiles)}),
            U as (
                UNPIVOT R ON {','.join(select_percentiles_columns)}
                INTO NAME P VALUE elapsed)
            select '{label or '*'}' as label, P::numeric as P, elapsed from U where P <> '100'
        """)
        return data
    def all_percentiles_sql(self, *, labels=[]):
        if not labels: labels = self.query("select distinct label from src order by 1")['label'].to_list()
        return ' union all '.join(
            f'({self.percentiles_sql(label)})'
            for label in labels)
    def percentiles(self, labels=[]):
        data = mo.sql(self.all_percentiles_sql(labels=labels))
        chart = alt.Chart(data).mark_line().encode(
            x='P:T',
            y='elapsed:Q',
            color='label:N'
        ).properties(width='container')
        return mo.ui.altair_chart(chart)

class WorkSeries:
    def __init__(self, defs, create_workset=None):
        self.defs = defs
        if create_workset is None: create_workset = WorkSet
        self.sets = { k: create_workset(scope) for (k, scope) in defs.items() }
    @cached_property
    def api(self):
        return WorkSeries(self.defs, lambda d: WorkSet(d).api)
    @cached_property
    def ui(self):
        return WorkSeries(self.defs, lambda d: WorkSet(d).ui)
    def error_rates(self):
        t = None
        for (k, v) in self.sets.items():
            tn = v.error_rates().rename(columns={'%err': f'@{k}'})[['label', f'@{k}']]
            t = tn if t is None else pd.merge(t, tn, how='outer')
        return t
    def response_times(self, column='p95'):
        t = None
        for (k, v) in self.sets.items():
            tn = v.response_times().rename(columns={column: f'@{k}'})[['label', f'@{k}']]
            t = tn if t is None else pd.merge(t, tn, how='outer')
        return t
