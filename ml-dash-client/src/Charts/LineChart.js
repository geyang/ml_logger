import React, {Fragment, useState, useEffect} from 'react';
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {
  AreaSeries,
  LineSeries,
  LineSeriesCanvas,
  FlexibleXYPlot,
  HorizontalGridLines,
  XAxis,
  YAxis,
  Crosshair
} from "react-vis";
import 'react-vis/dist/style.css';
import DataFrame from "dataframe-js";
import {modernEnvironment} from "../data";
import Color from 'color';
import {chartColors} from "./chart-theme";

const seriesQuery = graphql`
    query LineChartsQuery(
    $prefix: String,
    $xKey: String,
    $xAlign: String,
    $yKey: String,
    $yKeys: [String],
    $k: Int,
    $metricsFiles: [String]!
    ) {
        series (
            metricsFiles: $metricsFiles
            prefix: $prefix
            k: $k
            xKey: $xKey
            yKey: $yKey
            yKeys: $yKeys
            xAlign: $xAlign
            # k: 10                    
        ) {id xKey yKey xData yMean y25 y75}
    }
`;

function fetchSeries({metricsFiles, prefix, xKey, xAlign, yKey, yKeys, k,}) {
  return fetchQuery(modernEnvironment, seriesQuery, {metricsFiles, prefix, xKey, xAlign, yKey, yKeys, k});
}

function seriesToRecords(series) {
  if (!series || !series.yMean)
    return [];
  const df = new DataFrame({
    y: series.yMean,
    x: series.xData ? series.xData : series.yMean.map((_, i) => i)
  });
  return df
      .filter(row => row.get('y') === row.get('y'))
      .toCollection();
}

function seriesToAreaRecords(series) {
  if (!series || !series.y75 || !series.y25)
    return [];
  const df = new DataFrame({
    y0: series.y75,
    y: series.y25,
    x: series.xData ? series.xData : series.y25.map((_, i) => i)
  });
  return df
      .filter(row => row.get('y') === row.get('y') && row.get('y0') === row.get('y0'))
      .toCollection();
}

function time(v) {
  let s = new Date(v / 1000).toLocaleTimeString();
  return s.slice(0, s.length - 3)
}

function LineChart({
                     metricsFiles,
                     prefix,
                     xKey, yKey, yKeys,
                     xFormat, yFormat,
                     xTitle, yTitle,
                     k = 20,
                     color = chartColors.red,
                     ..._props
                   }) {

  const [crosshairValues, setCrosshairValues] = useState([]);

  const [lines, setLines] = useState([]);

  function _onMouseLeave() {
    setCrosshairValues([]);
  }

  function _onNearestX(value, {object, index}) {
    setCrosshairValues(lines.map(d => ({
      "value": d.mean[index],
      "mean": d.mean[index].y,
      "25%": d.quarter[index].y,
      "75%": d.quarter[index].y0,
    })));
  }

  useEffect(() => {
    if (!lines.length) fetchSeries({metricsFiles, prefix, xKey, yKey, yKeys, k})
        .then(({series}) => setLines([
          {
            mean: seriesToRecords(series),
            quarter: seriesToAreaRecords(series)
          }
        ]));
  }, [metricsFiles, prefix, xKey, yKey, yKeys, k]);

  return <FlexibleXYPlot onMouseLeave={_onMouseLeave} {..._props}>
    {lines.map((line, i) =>
        [(line.quarter.length > 100)
            ? null // do not show area if there are a lot of points. As an optimization.
            : <AreaSeries data={line.quarter}
                          style={{
                            stroke: Color(color).alpha(0.4).rgb().string(),
                            strokeWidth: 0.5,
                            fill: Color(color).alpha(0.2).rgb().string()
                          }}/>,
          (line.mean.length < 50)
              ? <LineSeries data={line.mean} stroke={color} strokeWidth={2} onNearestX={_onNearestX}/>
              : <LineSeriesCanvas data={line.mean} stroke={color} strokeWidth={2} onNearestX={_onNearestX}/>
        ]
    )}
    <YAxis tickFormat={yFormat === 'time' ? time : null}
           title={yTitle || yKey}
           style={{text: {background: "white", fontWeight: 800}}}/>
    <XAxis tickLabelAngle={-35}
           tickFormat={xFormat === 'time' ? time : null}
           title={xTitle || xKey}
           style={{text: {background: "white", fontWeight: 800}}}/>
    {crosshairValues.length
        ? <Crosshair values={crosshairValues.map(_ => _.value)}>
          <div style={{
            background: "#333538",
            display: "block",
            color: 'white',
            padding: "7px",
            whiteSpace: "nowrap",
            lineHeight: "14px",
            borderRadius: "10px",
            textAlign: "right"
          }}>
            <strong>{
              (xFormat === "time")
                  ? time(crosshairValues[0].value.x)
                  : crosshairValues[0].value.x
            }</strong>
            <br/>
            {yKey}: {crosshairValues[0].value.y.toFixed(3)
          }</div>
        </Crosshair>
        : null}
  </FlexibleXYPlot>

}

export default LineChart;
