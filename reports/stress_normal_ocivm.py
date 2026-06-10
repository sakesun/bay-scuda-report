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
    ws = WorkSet(filter_for_range([2026, 5, 23,  1, 00], [2026, 5, 23,  4, 00]))
    series = WorkSeries({
        '200': filter_for_range([2026, 5, 23,  1, 00], [2026, 5, 23,  1, 10]),
        '210': filter_for_range([2026, 5, 23,  1, 15], [2026, 5, 23,  1, 25]),
        '220': filter_for_range([2026, 5, 23,  1, 30], [2026, 5, 23,  1, 40]),
        '230': filter_for_range([2026, 5, 23,  1, 45], [2026, 5, 23,  1, 55]),
        '240': filter_for_range([2026, 5, 23,  2, 00], [2026, 5, 23,  2, 10]),
        '250': filter_for_range([2026, 5, 23,  2, 15], [2026, 5, 23,  2, 25]),
        '260': filter_for_range([2026, 5, 23,  2, 30], [2026, 5, 23,  2, 40]),
        '270': filter_for_range([2026, 5, 23,  2, 45], [2026, 5, 23,  2, 55]),
        '280': filter_for_range([2026, 5, 23,  3, 00], [2026, 5, 23,  3, 10]),
        '290': filter_for_range([2026, 5, 23,  3, 15], [2026, 5, 23,  3, 25]),
        '300': filter_for_range([2026, 5, 23,  3, 30], [2026, 5, 23,  3, 40])
    })
    return series, ws


@app.cell
def _(ws):
    ws.show_sources()
    return


@app.cell
def _(ws):
    ws.api.response_times()
    return


@app.cell
def _(series):
    series.api.error_rates()
    return


@app.cell
def _(series):
    series.api.response_times('p95')
    return


@app.cell
def _(series):
    series.api.response_times('p90')
    return


@app.cell
def _(series):
    series.ui.response_times('p90')
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
    ws.api.timeline_response_times()
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
