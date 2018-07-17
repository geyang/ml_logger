import React, {Component} from 'react'
import {getKeysFromRecords, matchExp, recordsToSeries} from "../data-helpers";
import selector from "../lib/react-luna";
import {uriJoin} from "../lib/file-api";

// takes in dataKey, chartKey and a charting component. Outputs the chart.
class _ChartDataContainer extends Component {
    state = {
        records: [],
        serieses: []
    };

    static getDerivedStateFromProps(props, state) {
        const {metricRecords, dataKey, chartKey, xKey = "_step"} = props;
        const records = metricRecords[dataKey];
        if (!state.records && !records) return null;
        if (state.records !== records) {
            if (!records) return {records: [], serieses: []};
            // } else if (this.state.records !== records && !(!this.state.records && !records)) {
            const keys = getKeysFromRecords(records);
            let serieses = keys.filter(matchExp(chartKey)).map(key => recordsToSeries(records, key, xKey));
            return {records, serieses: serieses || []};
        }
        return null;
    }

    render() {
        const {children, component: Component, ...props} = this.props;
        const {serieses} = this.state;
        return <Component serieses={serieses} {...props}>{children}</Component>;
    }
}


export const ChartDataContainer = selector(
    ({metricRecords}) => ({metricRecords}),
    _ChartDataContainer
);

class _ComparisonDataContainer extends Component {
    state = {
        chartKey: null,
        dataKeys: [],
        records: {},
        serieses: []
    };

    static getDerivedStateFromProps(props, state) {
        // caching here is a bit non-trivial.
        // todo: make the state update here more efficient.
        const {metricRecords, dataKeys, chartKey, xKey = "_step"} = props;
        let dirty = false;
        let newDataKeys, newChartKey, newRecords = {};
        if (chartKey !== state.chartKey) dirty = true;
        if (dataKeys.join(',') !== state.dataKeys.join(',')) dirty = true;
        newChartKey = chartKey;
        newDataKeys = dataKeys;
        dataKeys.forEach(dataKey => {
            const records = metricRecords[dataKey];
            newRecords[dataKey] = records;
            if (records !== state.records[dataKey]) dirty = true;
        });
        if (!dirty) return null;
        let serieses = [];
        dataKeys.forEach(dataKey => {
            const records = metricRecords[dataKey];
            if (records) {
                const keys = getKeysFromRecords(records);
                keys.filter(matchExp(chartKey)).forEach(key =>
                    // todo: insert logic to make dataKey shorter.
                    serieses.push(recordsToSeries(records, key, xKey, uriJoin(dataKey, key))))
            }
        });
        return {dataKeys: newDataKeys, chartKey: newChartKey, records: newRecords, serieses}
    }

    render() {
        const {children, component: Component, ...props} = this.props;
        const {serieses} = this.state;
        return <Component serieses={serieses} {...props}>{children}</Component>;
    }
}


export const ComparisonDataContainer = selector(
    ({metricRecords}) => ({metricRecords}),
    _ComparisonDataContainer
);
