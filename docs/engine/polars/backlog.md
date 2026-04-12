# MacroPipe backlog

## Iteration +1

- More primitives: fill_null, drop_nans, drop_nulls, fill_nan
- Manipulation of nested data (slicing, reformatting) (JSON Path?)
  https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.json_path_match.html
- Use polars-url, polars-ts, turtle-island
  https://github.com/ddotta/awesome-polars

## Iteration +2

- The implementation is currently doing pipe littering across the board. Please optimize!
  https://docs.pola.rs/user-guide/migration/pandas/#pipe-littering
- Insights into working with `try_parse_dates`.
  https://docs.pola.rs/user-guide/transformations/time-series/filter/
- What about multi-stage pipelines?
  https://docs.pola.rs/polars-cloud/integrations/airflow/#parallel-query-execution
- What about resampling?
  https://docs.pola.rs/user-guide/transformations/time-series/resampling/
- Timezones?
  https://docs.pola.rs/user-guide/transformations/time-series/timezones/
