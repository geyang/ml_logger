import React, {Component} from 'react'
import {getKeysFromRecords, matchExp, recordsToSeries} from "../data-helpers";
import selector from "../lib/react-luna";
import {markDirty, uriJoin} from "../lib/file-api";


// takes in dataKey, chartKey and a charting component. Outputs the chart.
export class ChartToSeries extends Component {
    state = {
        records: null,
        serieses: []
    };


    static getDerivedStateFromProps(props, state) {
        const {records, chartKey, xKey = "_step"} = props;
        if (state.records !== records) {
            if (!records) return {records: [], serieses: []};
            // } else if (this.state.data !== data && !(!this.state.data && !data)) {
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


function sharedPrefix(array) {
    if (!array || array.length === 0) return '';
    //this prevents mutation of the array;
    let A = array.concat().sort();
    let a1 = A[0];
    let a2 = A[A.length - 1];
    let L = Math.min(a1.length, a2.length);
    let i = 0;
    while (i < L && a1.charAt(i) === a2.charAt(i))
        i++;
    return a1.substring(0, i);
}

function sharedPostfix(array) {
    if (!array || array.length === 0) return '';
    //this prevents mutation of the array;
    let A = array.map(s => [...s].reverse().join('')).sort();
    let a1 = A[0];
    let a2 = A[A.length - 1];
    let L = Math.min(a1.length, a2.length);
    let i = 0;
    while (i < L && a1.charAt(i) === a2.charAt(i))
        i++;
    return [...a1.substring(0, i)].reverse().join('');
}

function removeSharedStart(array) {
    let prefix = sharedPrefix(array);
    return array.map(str => str.slice(prefix.length));
}

function removeAlphabeticalPostfix(string) {
    let match = string.match(/[A-z0-9]*$/);
    let newLength = match ? match[0].length : undefined;
    // has to be undefined. with `null` slice ends at 0.
    return string.slice(0, newLength ? -newLength : undefined)
}

//trying to implement shorter legend.
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
            const {records} = metricRecords[dataKey] || {};
            newRecords[dataKey] = records;
            if (records !== state.records[dataKey]) dirty = true;
        });
        if (!dirty) return null;
        let serieses = [];
        let prefix = removeAlphabeticalPostfix(sharedPrefix(dataKeys));
        let postfix = sharedPostfix(dataKeys);
        dataKeys.forEach(dataKey => {
            const {records} = metricRecords[dataKey] || {};
            let shortKey = dataKey.slice(prefix.length, (postfix.length) ? -postfix.length : undefined);
            if (records) {
                const keys = getKeysFromRecords(records);
                keys.filter(matchExp(chartKey)).forEach(key =>
                    // todo: insert logic to make dataKey shorter.
                    serieses.push(recordsToSeries(records, key, xKey, uriJoin(shortKey, key))))
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
