import React, {useEffect, useState} from "react";
import {Grid} from "../../components/layouts";
import InlineFile, {AnyChart, fetchAllCharts, fetchTextFile, fetchYamlFile, InlineChart} from "../../Charts/FileViews";
import {pathJoin} from "../../lib/path-join";
import InlineExperimentView from "../../Charts/InlineExperimentView";
import JSON5 from "json5";
import {colorMap} from "../../Charts/chart-theme";

function preproc(charts) {
  return (charts || [])
      .filter(c => c !== null)
      .map(c => (typeof c === 'string') ? {type: "series", yKey: c} : c)
      .filter(c => (!c.prefix && !c.metricsFiles))
      .map(c => ({...c, type: c.type || "series"}));
}

// function ChartView({
//                      id, dir, name, path,
//                      text,
//                      yaml: {metricsFile = null, metricsFiles = [], ...chart}
//                    }) {
//
//   const [showEdit, toggleEdit] = useToggle(false);
//
//   if (!metricsFile && !metricsFiles) {
//     metrics = path + "/metrics.pkl"
//   }
//
//   return <InlineChart key={JSON5.stringify(chart)}
//                       color={"#23aaff"}
//                       metricsFiles={metricsFile ? [metricsFile] : metricsFiles}
//                       {...chart} />;
// }

//highlevel interface:
export default function ChartGridView({path}) {
  const [charts, setCharts] = useState([])

  function _loadChart(path, i) {
    fetchYamlFile(path)
        .then(({node, errors}) => {
          if (!errors)
            setCharts((oldCharts) => [...oldCharts.slice(0, i), node, ...oldCharts.slice(i + 1)])
        });
  }

  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    if (!path) return abort;
    fetchAllCharts(path)
        .then(({node, errors}) => {
          if (running && node && node.charts && node.charts.edges)
            setCharts(node.charts.edges.map(({node: chart}) => chart))
        });
    return abort;
  }, [path]);

  return <Grid>
    {charts.map(({id, dir, path: configPath, yaml: chart}, i) =>
        <AnyChart key={i} configPath={configPath} onRefresh={() => _loadChart(configPath, i)}
                  prefix={dir} {...chart}/>)}
    <InlineExperimentView path={path}
                          addTextFile={true}
                          showHidden={true}
                          onClick={() => null}
        // addMetricCell={addMetricCell}
        // addChart={addChart}
    />
  </Grid>;
}
