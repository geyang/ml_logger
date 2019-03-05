import {DataFrame} from "pandas-js";

export function seriesToRecords(series) {
  const df = new DataFrame(series);
  return df.toRecords();
}

export function recordsToSeries(series) {
  const df = new DataFrame(series);
  return df.toRecords()
}
