import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from scuda import filter_for, filter_for_range, merge_filters, WorkSet, WorkSeries

    return WorkSet, filter_for


@app.cell
def _(WorkSet, filter_for):
    ws = WorkSet(filter_for(2026, 5, 27, 22, 00))
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
    ws.api.query('select * from src where not success')
    return


@app.cell
def _(ws):
    ws.api.query("select label, responseCode, avg(elapsed), count(*) from src where label = 'SearchJoint' group by all")
    return


@app.cell
def _(ws):
    ws.api.query("select * from src where label = 'SearchIndividual' order by elapsed desc")
    return


@app.cell
def _(ws):
    import marimo as _mo
    import altair as _alt
    _alt.data_transformers.enable("vegafusion")

    _bin = _alt.Bin(maxbins=20)

    _d    = ws.api.query("select * from src where label = 'SearchJoint'")
    _d500 = ws.api.query("select * from src where label = 'SearchJoint' and responseCode = '500'")
    _d200 = ws.api.query("select * from src where label = 'SearchJoint' and responseCode = '200'")

    _c500 = _alt.Chart(_d).transform_filter(
        _alt.datum.responseCode == '500'
    ).mark_bar(
        color='steelblue',
        opacity=0.1
    ).encode(
        x=_alt.X('elapsed:Q', bin=_bin),
        y='count():Q'
    )
    _c200 = _alt.Chart(_d200).transform_filter(
        _alt.datum.responseCode == '500'
    ).mark_bar(
        color='orange',
        opacity=0.9
    ).encode(
        x=_alt.X('elapsed:Q', bin=_bin),
        y='count():Q'
    )

    _combined = _c500 + _c200
    _combined.properties(title='hoho')
    return


@app.cell
def _(ws):
    _data = ws.api.query("select * from src where label = 'SearchJoint' and responseCode = '200'")
    import marimo as _mo
    import altair as _alt

    _alt.data_transformers.enable("vegafusion")
    # 2. Create the binned histogram
    _alt.Chart(_data).mark_point().encode(
        x=_alt.X('elapsed:Q', bin=True),
        y='count()'
    )
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
    ws.api.query('select count(*) from src')
    return


@app.cell
def _(ws):
    ws.api.timeline_error_rates()
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
    ws.ui.timeline_tps()
    return


@app.cell
def _(ws):
    ws.ui.timeline_response_times()
    return


@app.cell
def _(ws):
    ws.ui.error_rates()
    return


@app.cell
def _(ws):
    ws.ui.percentiles()
    return


if __name__ == "__main__":
    app.run()
