import React, {Fragment} from "react";
import LineChart from "../../Charts/LineChart";
import {Grid, Box, CheckBox} from "grommet";

function GridView({series, ...props}) {
  console.log(series);
  return <LineChart {...series} {...props}/>
}

function chartRegular(chartString) {
  if (typeof chartString === 'object')  // a bit dangerous
    return chartString;
  else if (chartString.startsWith('img:'))
    return {type: "image", yKey: chartString.slice(4)};
  else if (chartString.startsWith('mov:'))
    return {type: "image", yKey: chartString.slice(4)};
  else return {type: "line", yKey: chartString}
}

function ChartGrid({experiments, charts, relay, ..._props}) {
  console.log(experiments);
  console.log(charts);
  return <div>
    <Box justify="left" pad='small' height="36px" direction='row' align="start" fill='horizontal' gap='medium'
         height={56}>
      <Box as="h1">Comparison</Box>
      <Box as={CheckBox} label="by Row"/>
    </Box>
    <Grid fill={true} rows="small" columns="small">
      {experiments.map(({metrics}) => <Fragment key={metrics.path}>
            {charts
                .map(chartRegular)
                .filter(chart => chart.type === 'line')
                .map((chart) => {
                  let {metricsFiles, ..._chart} = chart;
                  metricsFiles = metricsFiles || [metrics.path];
                  return <Box key={chart.xKey}>
                    <LineChart metricsFiles={metricsFiles} {..._chart}/>
                  </Box>;
                })}
          </Fragment>
      )}
    </Grid>
  </div>
}


export default ChartGrid;
