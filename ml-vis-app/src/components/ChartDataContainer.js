import React from 'react'
import {recordsToSeries} from "../data-helpers";
import selector from "../lib/react-luna";

// takes in dataKey, chartKey and a charting component. Outputs the chart.
function ChartDataContainer(
    {metricRecords, dataKey, chartKey, xKey = "_step", children, component: Component}
) {
    let serieses = [];
    const records = metricRecords[dataKey];
    if (records) serieses = [recordsToSeries(records, chartKey, xKey)];
    return <Component serieses={serieses}>{children}</Component>;
}


export default selector(
    ({metricRecords}) => ({metricRecords}),
    ChartDataContainer
)
