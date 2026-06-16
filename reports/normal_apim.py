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

    return WorkSet, filter_for


@app.cell
def _(WorkSet, filter_for):
    ws = WorkSet(filter_for(2026, 5, 22, 22, 30))
    return (ws,)


@app.cell
def _(ws):
    ws.show_sources()
    return


@app.cell
def _(ws):
    ws.api.response_times()[['label', 'p90']]
    return


@app.cell
def _(ws):
    ws.api.timeline_error_rates()
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
    ws.api.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.api.percentiles()
    return


@app.cell
def _(ws):
    ws.ui.response_times()[['label', 'p90']]
    return


@app.cell
def _(ws):
    ws.ui.percentiles()
    return


@app.cell
def _(ws):
    ws.ui.timeline_response_times()
    return


if __name__ == "__main__":
    app.run()
