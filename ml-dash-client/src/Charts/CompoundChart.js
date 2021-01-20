import React, {Fragment, useState, useEffect} from 'react';
import graphql from "babel-plugin-relay/macro";
import {fetchQuery} from 'relay-runtime';
import 'react-vis/dist/style.css';
import {detect} from "detect-browser";
import DataFrame from "dataframe-js";
import {modernEnvironment} from "../data";
import Color from 'color';
import {chartColors, colorPalette} from "./chart-theme";
import {pathJoin} from "../lib/path-join";
import {fetchSeries, LinePlot, seriesToAreaRecords, seriesToRecords} from "./LineChart";

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


function time(v) {
  let s = new Date(v / 1000).toLocaleTimeString();
  return s.slice(0, s.length - 3)
}

function timeDelta() {
  //todo: add timeDelta formatter
}

export function numOfFacets({facet, metricsGroups = [], yKeys = []}) {
  if (facet === "group") return metricsGroups.length || 1;
  else return yKeys.length || 1;
}

export function numOfLines({facet, metricsGroups = [], yKeys = []} = {}) {
  if (facet === "group") return yKeys.length || 1
  else return metricsGroups.length || 1
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
                                        colors = colorPalette,
                                        ..._props
                                      }) {
  if (!!yKey) yKeys = [yKey];
  if (!groupLabels) groupLabels = [...Array(metricsGroups.length).keys()].map((i) => `group-${i}`);
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
      setCharts((charts) => ({...charts, [gKey]: []}));
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

  if (facet === "group") {
    return Object.keys(charts).map((gKey, i) => {
      let lines = charts[gKey];
      return <LinePlot key={gKey} title={groupLabels[i]} xLabels={xKey} yLabels={yKeys} xTitle={xTitle} yTitle={yTitle}
                       xFormat={xFormat} yFormat={yFormat} colors={colors} lines={lines} {..._props}/>
    })

  } else {
    //facet by yKey
    return yKeys.map((yKey, i) => {
      const lines = Object.keys(charts).map((k, gKey) => charts[k][i])
      // console.log("facet by key", Object.keys(charts), yKeys, lines, groupLabels)
      return <LinePlot key={i} xLabels={xKey} yLabels={groupLabels} xTitle={xTitle} yTitle={yKey}
                       xFormat={xFormat} yFormat={yFormat} colors={colors} lines={lines} {..._props}/>
    })
  }
}

