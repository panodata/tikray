# Changelog

## Unreleased
- CLI: Added CLI interface, per `tikray` program
- Core: Started using `orjson` and `orjsonl` packages, for performance
  reasons and JSONL/NDJSON support
- Core: Optionally invoke single resource on project file

## 2025/02/05 v0.0.23
- Renamed package to `loko`, then `tikray`

## 2024/09/26 v0.0.19
- Zyp/Moksha: Improve error reporting when rule evaluation fails

## 2024/09/25 v0.0.18
- Zyp/Moksha/jq: `to_object` function now respects a `zap` option, that
  removes the element altogether if it's empty
- Zyp/Moksha/jq: Improve error reporting at `MokshaTransformation.apply`

## 2024/09/22 v0.0.17
- Zyp: Added capability to skip rule evaluation when `disabled: true`

## 2024/09/19 v0.0.16
- Zyp: Fixed execution of collection transformation
- Zyp: Added software test and documentation about flattening lists
- Zyp: Translate a few special treatments to jq-based `MokshaTransformation` again

## 2024/09/10 v0.0.15
- Added Zyp Treatments, a slightly tailored transformation subsystem

## 2024/08/14 v0.0.4
- Added Zyp Transformations, a minimal transformation engine
  based on JSON Pointer (RFC 6901).
