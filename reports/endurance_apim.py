import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
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
    ws.get_ui("(label='CreateIndividualProfile.Occupation.AddOccupationInformation.Save') and success").timeline_response_times()
    return


@app.cell
def _(ws):
    import marimo as _mo
    import scuda as _scuda
    seven_hours = 7 * 60 * 60 * 1000
    starting = ws.ui.query("select max(epoch_ms(timeStamp)) ts from src where timeStamp < timestamp '2026-05-30 18:00:00.000' at time zone 'Asia/Bangkok'")['ts'][0] - seven_hours
    ending   = ws.ui.query("select min(epoch_ms(timeStamp)) ts from src where timeStamp > timestamp '2026-05-30 18:00:00.000' at time zone 'Asia/Bangkok'")['ts'][0] - seven_hours
    period = ending - starting
    _mo.sql(f"""
      select {starting} starting
           , {ending}   ending
           , to_timestamp({starting}/1000) at time zone 'UTC' starting_ts
           , to_timestamp({ending}  /1000) at time zone 'UTC' ending_ts
           , {period}
    """)
    return period, starting


@app.cell
def _(ws):
    import marimo as _mo
    import scuda as _scuda
    _mo.sql(_scuda.with_raw_src_from_files(ws.result_files, f"""
      select min(to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok') min_bkk
           , max(to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok') max_bkk
           , epoch_ms(min(to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok')) min_bkk_ts
           , min(timeStamp)                                                          min_ts
           , epoch_ms(max(to_timestamp(timeStamp/1000) AT TIME ZONE 'Asia/Bangkok')) max_bkk_ts
           , max(timeStamp)                                                          max_ts
           , (min_bkk_ts - min_ts)
           , (max_bkk_ts - max_ts)
        from src
    """, where=_scuda.IS_UI))

    return


@app.cell
def _(period, starting, ws):
    import marimo as _mo
    import scuda as _scuda
    _mo.sql(_scuda.with_raw_src_from_files(ws.result_files, f"""
      select timestamp: (timeStamp + {period + period})
           , elapsed, label, responseCode, responseMessage, threadName
           , dataType, success, failureMessage, bytes, sentBytes
           , grpThreads, allThreads, URL, Latency, IdleTime, Connect
        from src
        where src.timeStamp > {starting - period - period}
          and src.timeStamp < {starting - period}
        order by timeStamp
    """, where=_scuda.IS_UI))

    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    _df = mo.sql(
        f"""

        """
    )
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


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
