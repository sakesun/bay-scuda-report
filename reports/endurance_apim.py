import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from scuda import filter_for, filter_for_range, merge_filters, WorkSet, WorkSeries

    return WorkSet, filter_for_range


@app.cell
def _(WorkSet, filter_for_range):
    ws = WorkSet(filter_for_range([2026, 5, 30, 8, 45], [2026, 5, 30, 23, 45]))
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
    ws.api.error_rates()
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
    ws.ui.timeline_tps()
    return


@app.cell
def _(ws):
    ws.ui.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.get_ui("(label='CreateIndividualProfile.Occupation.AddOccupationInformation.Save') and success").timeline_response_times()
    return


@app.cell
def _(ws):
    ws.get_ui("(label='CreateJuristicProfile.Personal.Continue') and success").timeline_response_times()
    return


@app.cell
def _(ws):
    ws.get_ui("(label='CreateIndividualProfile.Completion') and success").timeline_response_times()
    return


@app.cell
def _(ws):
    ws.get_ui('true').ui.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.get_ui('true').timeline_error_rates()
    return


@app.cell
def _(ws):
    ws.ui.percentiles()
    return


if __name__ == "__main__":
    app.run()
