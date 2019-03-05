import React, {Fragment} from "react";
import LineChart from "../../Charts/LineChart";
import {Grid, Box} from "grommet";

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

class ChartGrid extends React.Component {

  render() {
    const {experiments, charts, relay, ...props} = this.props;
    console.log(experiments);
    console.log(charts);
    return <div>
      <h1>chart grid</h1>
      <Grid fill={true} rows="small" columns="small">
        {experiments.map(({metrics}) => <Fragment key={metrics.path}>
              {charts
                  .map(chartRegular)
                  .filter(chart => chart.type === 'line')
                  .map((chart) => {
                    let {metricsFiles, ..._chart} = chart;
                    metricsFiles = metricsFiles || [metrics.path];
                    console.log(metricsFiles);
                    return <Box key={chart.xKey}>
                      <LineChart metricsFiles={metricsFiles} {..._chart}/>
                    </Box>;
                  })}
            </Fragment>
        )}
      </Grid>
    </div>
  }
}


export default ChartGrid;
