import React, {useEffect, useState} from "react";
import {Grid} from "../../components/layouts";
import InlineFile, {fetchTextFile, fetchYamlFile, InlineChart} from "../../Charts/FileViews";
import {pathJoin} from "../../lib/path-join";
import InlineExperimentView from "../../Charts/InlineExperimentView";
import JSON5 from "json5";

function preproc(charts) {
  return (charts || [])
      .filter(c => c !== null)
      .map(c => (typeof c === 'string') ? {type: "series", yKey: c} : c)
      .filter(c => (!c.prefix && !c.metricsFiles))
      .map(c => ({...c, type: c.type || "series"}));
}


//highlevel interface:
export default function ChartGridView({expPath, chartsConfig}) {
  const chartPath = pathJoin(expPath, ".charts.yml");
  const metricsPath = pathJoin(expPath, "metrics.pkl");

  let [charts, setCharts] = useState([]);

  useEffect(() => {
    if (chartsConfig && chartsConfig.length) {
      setCharts(preproc(chartsConfig || []));
      return;
    }
    let running = true;
    const abort = () => running = false;
    fetchYamlFile(chartPath).then(({node, errors}) => {
      if (!!errors || !node || !node.yaml || typeof node.yaml.charts === 'function') return null;
      if (running) setCharts(preproc(node.yaml.charts || []))
    });
    return abort;
  }, [expPath, setCharts]);

  return <Grid>
    {charts.map(({type, ...chart}, i) => {
      switch (type) {
        case "series":
          //todo: add title
          return <InlineChart key={JSON5.stringify(chart)}
                              metricsFiles={
                                typeof metricsPath === 'string' ? [metricsPath]
                                    : (metricsPath || [])}
                              color="red" // color={colorMap(expIndex)}
                              {...chart} />;
        case "file":
        case "video":
        case "mov":
        case "movie":
        case "img":
        case "image":
          return <InlineFile key={i}
                             type={type}
                             cwd={expPath}
                             glob={chart.glob}
                             src={chart.src}
                             {...chart}/>;
        default:
          return null;
      }
    })}
    <InlineExperimentView path={expPath}
                          showHidden={true}
                          onClick={() => null}
        // addMetricCell={addMetricCell}
        // addChart={addChart}
    />
  </Grid>;
}
