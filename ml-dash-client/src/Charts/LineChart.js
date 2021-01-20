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
  Crosshair,
  ChartLabel
} from "react-vis";
import 'react-vis/dist/style.css';
import styled from 'styled-components';
import {detect} from "detect-browser";
import DataFrame from "dataframe-js";
import {modernEnvironment} from "../data";
import Color from 'color';
import {chartColors, colorPalette} from "./chart-theme";
import {pathJoin} from "../lib/path-join";

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
        ) {id xKey yKey xData yMean y25pc y75pc}
    }
`;

const browser = detect();

let labelStyles = {
  fontWeight: 900,
  textAnchor: "end"
};
if (browser && browser.name !== "safari")
  labelStyles = {
    ...labelStyles,
    fill: "black",
    stroke: "white",
    strokeWidth: "2px",
    paintOrder: "stroke"
  };
let yLabelStyles = {
  ...labelStyles,
  transform: 'rotate(-90 0 0) translate(0 -38)'
};

const StyledTitle = styled(ChartLabel)`
> text { 
  font-weight: 500;
  text-anchor: middle;
  font-size: 14px !important;
  fill: #444 !important;
  stroke: white;
  stroke-width: 2px;
  paint-order: stroke
}`;
const StyledLabelH = styled(ChartLabel)`
> text { 
  font-weight: 900;
  text-anchor: start;
  font-size: 12px;
  fill: ${props => props.fill} !important;
}`

export function fetchSeries({metricsFiles, prefix, xKey, xAlign, yKey, yKeys, k,}) {
  // const controller = new AbortController();
  // const signal = controller.signal;
  return fetchQuery(modernEnvironment, seriesQuery, {
    metricsFiles: metricsFiles.filter(_ => !!_),
    prefix, xKey, xAlign, yKey, yKeys, k
  });
}

export function seriesToRecords(series, yKey = null) {
  if (!series || !series.yMean)
    return [];
  let yData = yKey ? series.yMean[yKey] : series.yMean;
  const df = new DataFrame({
    y: yData,
    x: series.xData ? series.xData : yData.map((_, i) => i)
  });
  return df
      .filter(row => row.get('y') === row.get('y'))
      .toCollection();
}

export function seriesToAreaRecords(series, yKey = null) {
  if (!series || !series.y75pc || !series.y25pc)
    return [];
  let yData = yKey ? series.y75pc[yKey] : series.y75pc;
  const df = new DataFrame({
    y0: yData,
    y: yKey ? series.y25pc[yKey] : series.y25pc,
    x: series.xData ? series.xData : yData.map((_, i) => i)
  });
  return df
      .filter(row => row.get('y') === row.get('y') && row.get('y0') === row.get('y0'))
      .toCollection();
}

function time(v) {
  let s = new Date(v / 1000).toLocaleTimeString();
  return s.slice(0, s.length - 3)
}

function timeDelta() {
  //todo: add timeDelta formatter
}

export function LinePlot({title, xLabels: xLabel, yLabels, xTitle, yTitle, xFormat, yFormat, colors, lines, ..._props}) {
  const [crosshairValues, setCrosshairValues] = useState([]);

  function _onMouseLeave() {
    setCrosshairValues([]);
  }

  function _onNearestX(value, {object, index}) {
    setCrosshairValues(lines.map(({mean = [], quarter = []} = {}, i) => {
      let value = mean[index];
      let quat = quarter[index];
      return {
        value,
        color: colors[i % colors.length],
        label: yLabels[i],
        x: value ? value.x : null,
        mean: value ? value.y.toFixed(3) : "NaN",
        range: quat ? (0.5 * (quat.y0 - quat.y)).toFixed(3) : "NaN",
      };
    }));
  }

  return <FlexibleXYPlot onMouseLeave={_onMouseLeave}
                         margin={{
                           top: title ? 30 : 10,
                           right: (yLabels.length <= 3) ? 0 : 120
                         }} {..._props}>
    {lines.map(({quarter = [], mean = []} = {}, i) =>
        [(quarter.length > 100)
            ? null // do not show area if there are a lot of points. As an optimization.
            : <AreaSeries key={`area-${i}`}
                          data={quarter}
                          style={{
                            stroke: Color(colors[i % colors.length]).alpha(0.4).rgb().string(),
                            strokeWidth: 0.5,
                            fill: Color(colors[i % colors.length]).alpha(0.2).rgb().string()
                          }}/>,
          (mean.length <= 100)
              ? <LineSeries key={`line-${i}`} data={mean} stroke={colors[i % colors.length]}
                            strokeWidth={2} onNearestX={_onNearestX}/>
              : <LineSeriesCanvas key={i} data={mean} stroke={colors[i % colors.length]}
                                  strokeWidth={2} onNearestX={_onNearestX}/>
        ]
    )}
    <YAxis tickFormat={yFormat === 'time' ? time : null} tickPadding={0}
           style={{text: {background: "white", fontWeight: 800}}}/>
    <XAxis tickLabelAngle={-35}
           tickFormat={xFormat === 'time' ? time : null}
           style={{text: {background: "white", fontWeight: 800}}}/>
    {typeof (title) === 'string'
        ? <StyledTitle text={title} includeMargin={false} xPercent={0.5} yPercent={0.1}/>
        : null}
    {(yLabels.length <= 1)
        ? <ChartLabel text={yTitle || yLabels[0]}
                      includeMargin={false}
                      xPercent={0.05}
                      yPercent={title ? 0.3 : 0.12}
                      style={yLabelStyles}/>
        : yLabels.map((label, i) =>
            <StyledLabelH key={i}
                          text={label}
                          includeMargin={false}
                          xPercent={(yLabels.length <= 3) ? 0.05 : 1.1}
                          yPercent={0.12 * i + (title ? 0.3 : 0.12)}
                          fill={colors[i % colors.length]}/>)
    }
    <ChartLabel text={xTitle || xLabel}
                className="alt-x-label"
                includeMargin={false}
                xPercent={0.95}
                yPercent={title ? 1.17 : 1}
                style={labelStyles}/>
    {crosshairValues.length
        ? <Crosshair values={crosshairValues.map(_ => _.value)}>
          <table style={{
            // background: "#333538",
            background: "rgba(255,255,255,0.8)",
            display: "block",
            color: 'black',
            padding: "7px",
            whiteSpace: "nowrap",
            lineHeight: "14px",
            borderRadius: "10px",
          }}>
            <tbody>
            <tr>
              <td style={{textAlign: "right"}}><strong>{xLabel}</strong>:</td>
              <td>{
                (xFormat === "time") ? time(crosshairValues[0].x) : crosshairValues[0].x
              }</td>
            </tr>
            {
              crosshairValues.sort((a, b) => (b.mean - a.mean)).map(({mean, range, color, label}, i) =>
                  <tr key={i} style={{color}}>
                    <td style={{textAlign: "right"}}><strong>{label}</strong>:</td>
                    <td>{mean}±{range}</td>
                  </tr>)
            }
            </tbody>
          </table>
        </Crosshair> : null}
  </FlexibleXYPlot>
}

export default function LineChart({
                                    prefix,
                                    metricsFile = null,
                                    metricsFiles = [],
                                    xKey,
                                    yKey, yKeys = [],
                                    xFormat, yFormat,
                                    xTitle, yTitle,
                                    xAlign,
                                    color,
                                    k = 20,
                                    colors = colorPalette,
                                    ..._props
                                  }) {
  if (!!yKey) yKeys = [yKey];
  if (!!metricsFile) metricsFiles = [metricsFile];

  const [lines, setLines] = useState([]);

  useEffect(() => {
    // if (!lines.length)
    let running = true;
    const abort = () => running = false;
    if (!metricsFiles) return abort;
    fetchSeries({metricsFiles, prefix, xKey, xAlign, yKeys, k})
        .then((data) => {
          if (!running || !data) return;
          if (!!yKeys) setLines(yKeys.map((k) => ({
            // yKey: k, // label the series
            mean: seriesToRecords(data.series, k),
            quarter: seriesToAreaRecords(data.series, k)
          })));
          else setLines([{
            mean: seriesToRecords(data.series),
            quarter: seriesToAreaRecords(data.series)
          }])
        });
    return abort;
  }, [prefix, ...metricsFiles, xKey, ...yKeys, k]);

  return <LinePlot xLabels={xKey} yLabels={yKeys} xTitle={xTitle} yTitle={yTitle}
                   xFormat={xFormat} yFormat={yFormat} colors={colors} lines={lines} {..._props}/>

}

