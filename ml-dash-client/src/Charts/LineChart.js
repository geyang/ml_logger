import React, {Fragment, useState, useEffect} from 'react';
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import {AreaSeries, LineSeries, FlexibleXYPlot, HorizontalGridLines, XAxis, YAxis, Crosshair} from "react-vis";
import 'react-vis/dist/style.css';
import DataFrame from "dataframe-js";

import {modernEnvironment} from "../data";
import {chartColors} from "./chart-theme";
import Color from 'color';

const seriesQuery = graphql`
    query LineChartsQuery(
    $prefix: String,
    $xKey: String,
    $yKey: String,
    $yKeys: [String],
    $metricsFiles: [String]
    ) {
        series (
            metricsFiles: $metricsFiles
            prefix: $prefix
            k: 40
            xKey: $xKey
            yKey: $yKey
            yKeys: $yKeys
            xAlign: "start"
            # k: 10                    
        ) {id xKey yKey xData yMean y25 y75}
    }
`;

function fetchSeries({prefix, xKey, yKey, yKeys, metricsFiles}) {
  return fetchQuery(modernEnvironment, seriesQuery, {prefix, xKey, yKey, yKeys, metricsFiles});
}

function seriesToRecords(series) {
  const df = new DataFrame({
    y: series.yMean,
    x: series.xData ? series.xData : series.yMean.map((_, i) => i)
  });
  return df
      .filter(row => row.get('y') === row.get('y'))
      .toCollection();
}

function seriesToAreaRecords(series) {
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
    if (!lines.length) fetchSeries({
      prefix,
      metricsFiles,
      xKey,
      yKey,
      yKeys
    }).then(({series}) => setLines([
      {mean: seriesToRecords(series), quarter: seriesToAreaRecords(series)}
    ]));
  });

  return <FlexibleXYPlot onMouseLeave={_onMouseLeave} {..._props}>
    {lines.map((line, i) =>
        [
          <AreaSeries data={line.quarter}
                      style={{
                        stroke: Color(chartColors.red).alpha(0.4).rgb().string(),
                        strokeWidth: 0.5,
                        fill: Color(chartColors.red).alpha(0.2).rgb().string()
                      }}/>,
          <LineSeries data={line.mean} style={{stroke: chartColors.red, strokeWidth: 2}} onNearestX={_onNearestX}/>
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
          <div style={{background: "#e6e6e6", color: 'white', width: "80px", height: "60px"}}>
            <p>{(yFormat === "time")
                ? time(crosshairValues[0].value.x)
                : crosshairValues[0].value.x}<br/>
              y: {crosshairValues[0].value.y.toFixed(1)}</p>
          </div>
        </Crosshair>
        : null}
  </FlexibleXYPlot>

}

export default LineChart;
