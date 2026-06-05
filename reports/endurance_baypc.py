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

    return WorkSet, filter_for_range


@app.cell
def _(WorkSet, filter_for_range):
    ws = WorkSet(filter_for_range([2026, 5, 16, 21, 00], [2026, 5, 17, 12, 00]))
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
    ws.api.timeline_tps()
    return


@app.cell
def _(ws):
    ws.api.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.api.percentiles()
    return


@app.cell
def _(ws):
    ws.ui.response_times()
    return


@app.cell
def _(ws):
    ws.ui.percentiles()
    return


if __name__ == "__main__":
    app.run()
