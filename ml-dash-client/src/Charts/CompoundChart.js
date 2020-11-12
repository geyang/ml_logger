import React, {Fragment, useState, useEffect} from 'react';
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import 'react-vis/dist/style.css';
import {detect} from "detect-browser";
import DataFrame from "dataframe-js";
import {modernEnvironment} from "../data";
import Color from 'color';
import {chartColors} from "./chart-theme";
import {pathJoin} from "../lib/path-join";
import {fetchSeries, LinePlot} from "./LineChart";

const browser = detect();

let labelStyles = {
  fontWeight: 900,
  textAnchor: "end"
};
if (browser && browser.name !== "safari")
  labelStyles = {...labelStyles, fill: "black", stroke: "white", strokeWidth: "2px", paintOrder: "stroke",};
let yLabelStyles = {
  ...labelStyles,
  transform: 'rotate(-90 0 0) translate(0 -38)'
};

function seriesToRecords(series, yKey = null) {
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

function seriesToAreaRecords(series, yKey = null) {
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

export function numOfFacets(chart) {
  if (chart.facet === "group") return chart.metricsGroups.length
  else return chart.yKeys ? chart.yKeys.length : 1;
}

export default function CompoundChart({
                                        prefix,
                                        metricsFile = null,
                                        metricsFiles = [],
                                        metricsGroups = [],
                                        groupLabels = [],
                                        facet = null,
                                        xKey,
                                        yKey,
                                        yKeys,
                                        xFormat,
                                        yFormat,
                                        xTitle,
                                        yTitle,
                                        xAlign,
                                        color,
                                        k = 20,
                                        colors = [chartColors.blue, chartColors.red, chartColors.grey],
                                        ..._props
                                      }) {
  if (!!yKey) yKeys = [yKey];
  // if (!!metricsFile) metricsFiles = [metricsFile];
  // if (!!metricsFiles) metricsGroups = [metricsFiles];

  const [charts, setCharts] = useState({});

  useEffect(() => {
    // if (!lines.length)
    // let running = true;
    // const abort = () => running = false;
    // if (!metricsGroups) return abort;
    if (!metricsGroups) return;
    metricsGroups.forEach((metricsFiles, gKey) => {
      fetchSeries({metricsFiles, prefix, xKey, xAlign, yKeys, k})
          .then((data) => {
            // if (!running || !data) return;
            setCharts((charts) => ({
              ...charts,
              [gKey]: yKeys.map((k) => ({
                mean: seriesToRecords(data.series, k),
                quarter: seriesToAreaRecords(data.series, k)
              }))
            }))
          });
    })
    // return abort;
  }, [prefix, ...yKeys, k]);
  // console.log(charts)

  if (facet === "group") {
    return <>{
      Object.keys(charts).map((k, i) => {
        let lines = charts[k];
        // console.log("facet by group", Object.keys(charts), yKeys, k, i, lines)
        return <LinePlot key={i} xLabels={xKey} yLabels={yKeys} xTitle={xTitle} yTitle={yTitle}
                         xFormat={xFormat} yFormat={yFormat} colors={colors} lines={lines} {..._props}/>
      })
    }</>
  } else {
    //facet by yKey
    if (!!groupLabels) groupLabels = [...Array(metricsGroups.length).keys()].map((i) => `group-${i}`);
    return <>{
      yKeys.map((yKey, i) => {
        const lines = Object.keys(charts).map((k, gKey) => charts[k][i])
        // console.log("facet by key", Object.keys(charts), yKeys, lines, groupLabels)
        return <LinePlot key={i} xLabels={xKey} yLabels={groupLabels} xTitle={xTitle} yTitle={yKey}
                         xFormat={xFormat} yFormat={yFormat} colors={colors} lines={lines} {..._props}/>
      })
    }</>
  }
}

