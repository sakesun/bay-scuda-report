# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    from scuda import filter_for, filter_for_range, merge_filters, WorkSet, WorkSeries

    return WorkSeries, WorkSet, filter_for_range


@app.cell
def _(WorkSeries, WorkSet, filter_for_range):
    ws = WorkSet(filter_for_range([2026, 5, 26, 22, 20], [2026, 5, 27, 1, 45]))
    series = WorkSeries({
        '250': filter_for_range([2026, 5, 26, 22, 20], [2026, 5, 26, 22, 30]),
        '270': filter_for_range([2026, 5, 26, 22, 35], [2026, 5, 26, 22, 45]),
        '290': filter_for_range([2026, 5, 26, 22, 50], [2026, 5, 26, 23, 00]),
        '310': filter_for_range([2026, 5, 26, 23,  5], [2026, 5, 26, 23, 15]),
        '330': filter_for_range([2026, 5, 26, 23, 20], [2026, 5, 26, 23, 30]),
        '350': filter_for_range([2026, 5, 26, 23, 35], [2026, 5, 26, 23, 45]),
        '370': filter_for_range([2026, 5, 26, 23, 50], [2026, 5, 27,  0, 00]),
        '390': filter_for_range([2026, 5, 27,  0,  5], [2026, 5, 27,  0, 15]),
        '410': filter_for_range([2026, 5, 27,  0, 20], [2026, 5, 27,  0, 30]),
        '430': filter_for_range([2026, 5, 27,  0, 35], [2026, 5, 27,  0, 45]),
        '450': filter_for_range([2026, 5, 27,  0, 50], [2026, 5, 27,  1, 00]),
        '470': filter_for_range([2026, 5, 27,  1,  5], [2026, 5, 27,  1, 15]),
        '490': filter_for_range([2026, 5, 27,  1, 20], [2026, 5, 27,  1, 30]),
        '510': filter_for_range([2026, 5, 27,  0, 35], [2026, 5, 27,  1, 45])
    })
    return series, ws


@app.cell
def _(ws):
    ws.show_sources()
    return


@app.cell
def _(ws):
    ws.api.response_times()[['label', 'min', 'avg', 'p95', 'cnt']]
    return


@app.cell
def _(ws):
    ws.api.error_rates()
    return


@app.cell
def _(series):
    series.api.error_rates()
    return


@app.cell
def _(series):
    series.api.response_times('avg')
    return


@app.cell
def _(series):
    series.api.response_times('p95')
    return


@app.cell
def _(series):
    series.ui.response_times('p95')
    return


@app.cell
def _(series):
    series.ui.error_rates()
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
             , max(elapsed) as elapsed
          from src
          group by all""")
    toplot
    return


@app.cell
def _(ws):
    ws.api.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.api.timeline_tps()
    return


@app.cell
def _(ws):
    ws.api.timeline_error_rates()
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
