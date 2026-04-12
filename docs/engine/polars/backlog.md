---
orphan: true
---

# MacroPipe backlog

## Iteration +1

- Allow registering functions under different names / aliases.
- Unlock using regular expressions directly on columns, using
  a special syntax like `col=foo:expr:arg1,arg2`.
- Add sorting for standalone use. When importing into a database, you don't
  necessarily need it, but of course in many other cases.
- Optimize [pipe littering] across the board.
- Map more primitives: fill_null, drop_nans, drop_nulls, fill_nan.
- Manipulation of nested data (slicing, reformatting), using [json_path_match].

## Iteration +2

- Use `responder` for a basic example to provide a HTTP interface to
  a Polars dataframe.
- How to sample random records?
- Map or wrap recipes from polars-url, polars-ts, turtle-island, see [awesome-polars].

## Iteration +3

- Insights into working with `try_parse_dates`.

  https://docs.pola.rs/user-guide/transformations/time-series/filter/
- What about multi-stage pipelines?

  https://docs.pola.rs/polars-cloud/integrations/airflow/#parallel-query-execution
- What about resampling?

  https://docs.pola.rs/user-guide/transformations/time-series/resampling/
- Timezone manipulation?

  https://docs.pola.rs/user-guide/transformations/time-series/timezones/


[awesome-polars]: https://github.com/ddotta/awesome-polars
[json_path_match]: https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.str.json_path_match.html
[pipe littering]: https://docs.pola.rs/user-guide/migration/pandas/#pipe-littering
