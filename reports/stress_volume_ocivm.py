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
    ws = WorkSet(filter_for_range([2026, 5, 28,  2, 00], [2026, 5, 28, 5, 15]))
    series = WorkSeries({
        '250': filter_for_range([2026, 5, 28,  2, 00], [2026, 5, 28,  2, 10]),
        '270': filter_for_range([2026, 5, 28,  2, 15], [2026, 5, 28,  2, 25]),
        '290': filter_for_range([2026, 5, 28,  2, 30], [2026, 5, 28,  2, 40]),
        '310': filter_for_range([2026, 5, 28,  2, 45], [2026, 5, 28,  2, 55]),
        '330': filter_for_range([2026, 5, 28,  3, 00], [2026, 5, 28,  3, 10]),
        '350': filter_for_range([2026, 5, 28,  3, 15], [2026, 5, 28,  3, 25]),
        '370': filter_for_range([2026, 5, 28,  3, 30], [2026, 5, 28,  3, 40]),
        '390': filter_for_range([2026, 5, 28,  3, 45], [2026, 5, 28,  3, 55]),
        '410': filter_for_range([2026, 5, 28,  4, 00], [2026, 5, 28,  4, 10]),
        '430': filter_for_range([2026, 5, 28,  4, 15], [2026, 5, 28,  4, 25]),
        '450': filter_for_range([2026, 5, 28,  4, 30], [2026, 5, 28,  4, 40]),
        '470': filter_for_range([2026, 5, 28,  4, 45], [2026, 5, 28,  4, 55]),
        '490': filter_for_range([2026, 5, 28,  5, 00], [2026, 5, 28,  5, 10]),
        '510': filter_for_range([2026, 5, 28,  5, 15], [2026, 5, 28,  5, 25])
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


@app.cell
def _(ws):
    ws.get_ui("(label='CreateIndividualProfile.Occupation.AddOccupationInformation.Save') and success").timeline_response_times()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
