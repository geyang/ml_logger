import {take, dispatch, ERROR_CALLBACK, THEN_CALLBACK, spawn, delay, call, select} from 'luna-saga';
import {recordsToSeries} from "../data-helpers";
import {stringify} from "query-string";
import {status200} from "./fetch-helper";
import {PUSH_LOCATION} from "./routeStoreConnect";
import {combineReducers} from "luna";

//helper functions
export function uriJoin(...chunks) {
    let root = "";
    for (let chunk of chunks) {
        if (!root) {
            root += chunk;
        } else if (root.endsWith('/') && chunk.startsWith('/')) {
            root += chunk.slice(1);
        } else if (root.endsWith('/') || chunk.startsWith('/')) {
            root += chunk;
        } else {
            root += '/' + chunk;
        }
    }
    return root;
}

export function parentDir(path) {
    let slashInd = path.lastIndexOf('/');
    return path.slice(0, slashInd > -1 ? slashInd : 0);
}

//file api
export class FileApi {
    constructor(server = "") {
        this.configure(server);
    }

    configure(server = "") {
        this.serverUri = server;
        this.fileEndpoint = `${this.serverUri}/files`;
        this.fileEvents = `${this.serverUri}/file-events`;
    }

    getFiles(currentDirectory = "/", query = "", recursive = false, stop = 10, start = 0) {
        let uri = `${this.fileEndpoint}${currentDirectory}`;
        const params = {};
        if (!!query) params.query = query;
        if (!!recursive) params.recursive = 1;
        if (!!start) params.start = start;
        if (!!stop) params.stop = stop;
        if (!!params) uri += `?${stringify(params)}`;
        return fetch(uri).then(status200).then(j => j.json())
    }

    subscribeFileEvents(currentDirectory = "/", query = "") {
        let uri = uriJoin(this.fileEvents, currentDirectory);
        const params = {};
        if (!!query) params.query = query;
        if (!!params) uri += `?${stringify(params)}`;
        return fetch(uri).then(status200).then(j => j.json());
    }

    getMetricData(path) {
        const src = uriJoin(this.fileEndpoint, path) + "?json=1";
        return fetch(src, {headers: {'Content-Type': 'application/json; charset=utf-8'}})
            .then(status200)
            .then((r) => r.json())
        // .then((d) => recordsToSeries(d));
    }

    deletePath(path) {
        const src = uriJoin(this.fileEndpoint, path);
        // console.log(src);
        return fetch(src, {method: "DELETE",}).then(status200)
    }

    static recordToSeries(metricRecords, experimentKeys, yKeys, xKey) {
        const series = [];
        experimentKeys.forEach(eKey => {
            metricRecords.forEach((records, _experimentKey) => {
                if (_experimentKey.match(eKey)) series.push();
            })
        });

    }
}

export const defaultState = {
    currentDirectory: "/",
    searchQuery: "",
    showComparison: false,
    showConfig: false,
};

export function ValueReducer(namespace = "", defaultState = null) {
    return function arrayReducer(state = defaultState, action) {
        if (action.type === `${namespace}_SET`) {
            return action.value
        }
        return state;
    }
}

export function ArrayReducer(namespace = "", defaultState = null) {
    return function arrayReducer(state = defaultState, action) {
        if (action.type === `${namespace}_PUSH`) {
            return [...state, action.item]
        } else if (action.type === `${namespace}_DELETE`) {
            return [...state.slice(0, action.ind), ...state.slice(action.ind + 1)]
        } else if (action.type === `${namespace}_MOVE`) {
            let _ = [...state.slice(0, action.ind), ...state.slice(action.ind + 1)];
            _.splice(action.newInd, 0, state[action.ind]);
            return _;
        } else if (action.type === `${namespace}_SET`) {
            return action.items
        }
        return state;
    }
}

export function goTo(path) {
    return {type: 'GO_TO', path};
}

export function queryInput(query) {
    return {type: 'SET_QUERY', query};
}

export function removePath(path) {
    return {type: 'REMOVE_PATH', path};
}

export function Files(reducerKey) {
    return function fileReducer(state = [], action) {
        if (action.type === `${reducerKey}_APPEND`) {
            // todo: remove dupes.
            return [...state, ...action.data];
        } else if (action.type === `${reducerKey}_ASSIGN`) {
            // todo: remove dupes.
            return action.data;
        } else if (action.type === `${reducerKey}_SORT`) {
            let files = [...state];
            if (action.sortBy === "modification") {
                files = files.sort((a, b) => a.mtime > b.mtime)
            } else if (action.sortBy === "creation") {
                files = files.sort((a, b) => a.ctime > b.ctime)
            } else if (action.sortBy === "prefix") {
                files = files.sort((a, b) => a.name > b.name)
            } else if (action.sortBy === "postfix") {
                files = files.sort((a, b) =>
                    a.name.split('').reverse().join('') > b.name.split('').reverse().join(''))
            }
            if (action.order === -1) {
                files = files.reverse()
            }
            return files;
        }
        return state
    }
}

const _fileReducer = combineReducers({
    files: Files('FILES'),
    metrics: Files('METRICS'),
    metricRecords: MetricRecordsReducer(),
    chartKeys: ArrayReducer("CHARTKEYS", ["loss.*", ".*"]),
    // todo: absorb this into the chart definition, as part of chartConfig object.
    yMin: ValueReducer('Y_MIN', null),
    yMax: ValueReducer('Y_MAX', null),
    filteredMetricsFiles: ValueReducer('FILTERED_METRIC_FILES', []),
    filteredFiles: ValueReducer('FILTERED_FILES', []),
});

export function setYMax(value) {
    return {
        type: "Y_MAX_SET",
        value
    }
}

export function setYMin(value) {
    return {
        type: "Y_MIN_SET",
        value
    }
}

export function insertChartKey(chartKey) {
    return {type: "CHARTKEYS_PUSH", item: chartKey}
}

export function deleteChartKey(index) {
    return {type: "CHARTKEYS_DELETE", ind: index}
}

export function moveChartKey(index, newIndex) {
    return {type: "CHARTKEYS_MOVE", ind: index, newInd: newIndex}
}

function fileReducer(state = defaultState, action) {
    if (action.type === "SET_QUERY") {
        return {...state, searchQuery: action.query};
    } else if (action.type === "TOGGLE_COMPARISON") {
        return {...state, showComparison: !state.showComparison}
    } else if (action.type === "TOGGLE_CONFIG") {
        return {...state, showConfig: !state.showConfig}
    } else if (action.type === "GO_TO") {
        let {path} = action;
        let {currentDirectory} = state;
        if (currentDirectory.endsWith('/')) currentDirectory = currentDirectory.slice(0, -1);
        while (path.match(/[./].*/)) {
            if (path.startsWith('../')) {
                currentDirectory = parentDir(currentDirectory);
                path = path.slice(3);
            } else if (path.startsWith('./')) {
                currentDirectory = parentDir(currentDirectory);
                path = path.slice(2);
            } else if (path.startsWith('/')) {
                currentDirectory = path;
                path = "";
            }
        }
        if (!!path) currentDirectory = uriJoin(currentDirectory, path);
        state = _fileReducer({...state, currentDirectory}, action);
        return state
    }
    return _fileReducer(state, action);
}

export function* searchProc() {
    let state, action, searchQuery, currentDirectory, metrics, files, metricRecords;
    while (true) {
        yield take(/(UPDATE_SEARCH_RESULTS|SET_QUERY)/);
        yield call(delay, 200);
        ({searchQuery, currentDirectory, metrics, files} = yield select());
        let filteredMetrics = metrics.filter(f => uriJoin(currentDirectory, f.path).match(searchQuery));
        ({state: {metricRecords, currentDirectory}} = yield dispatch({
            type: "FILTERED_METRIC_FILES_SET",
            value: filteredMetrics
        }));
        let dataKey;
        for (let file of filteredMetrics) {
            dataKey = uriJoin(currentDirectory, file.path);
            //only run once
            if (typeof metricRecords[dataKey] === 'undefined') {
                yield dispatch(markDirty(dataKey));
                // console.log(`dirtying ${dataKey}`)
            }
        }
        yield dispatch({
            type: "FILTERED_FILES_SET",
            value: files.filter(f => uriJoin(currentDirectory, f.path).match(searchQuery))
        });
    }

}

export function toggleComparison() {
    return {
        type: "TOGGLE_COMPARISON"
    }
}

export function toggleConfig() {
    return {
        type: "TOGGLE_CONFIG"
    }
}

// export const rootReducer = (state, action) => fileReducer(_fileReducer(state, action), action);
export const rootReducer = fileReducer;

const apiRoot = "http://54.71.92.65:8082";
export const fileApi = new FileApi(apiRoot);

export function* locationProc() {
    let state, action;
    while (true) {
        ({state, action} = yield take(PUSH_LOCATION));
        console.log(action.location);
        // yield dispatch(goTo())
    }
}

export function* removeProc() {
    let state, action, res;
    while (true) {
        ({state, action} = yield take("REMOVE_PATH"));
        res = yield fileApi.deletePath(action.path);
        // dispatch({
        //     type: "G"
        // })
    }

}

export function* directoryProc() {
    // add while true loop
    let state, action;
    while (true) {
        ({state, action} = yield take("GO_TO"));
        let files;
        try {
            files = yield fileApi
                .getFiles(state.currentDirectory, "*", false, 1000)
            // .catch(yield ERROR_CALLBACK);
        } catch (e) {
            console.error(e);
        }
        ({state, action} = yield dispatch({
            type: "FILES_ASSIGN",
            data: files
        }));
        ({state, action} = yield dispatch({
            type: "SORT_FILES",
            sortBy: "creation",
            order: -1
        }));
        yield dispatch({type: "UPDATE_SEARCH_RESULTS"})
    }
}

//this is only needed for the metrics data b/c we want to plot them over.
//might also need for text files.
function MetricRecordsReducer() {
    return function metricReducer(state = {}, action) {
        if (action.type === "SET_METRIC") {
            state = {...state, [action.key]: {records: action.records}};
            return state
        } else if (action.type === "REMOVE_METRIC") {
            state = {...state};
            delete state[action.key];
            return state;
        } else if (action.type === 'DIRTY') {
            let record = state[action.key];
            return {...state, [action.key]: {...record, dirty: true}}
        } else if (action.type === 'FETCHING_METRIC_DATA') {
            let record = state[action.key];
            return {...state, [action.key]: {...record, fetching: true}}
        }
        return state
    }
}

export function markDirty(experimentKey) {
    return {
        type: "DIRTY",
        key: experimentKey
    }
}

export function markDownloading(experimentKey) {
    return {
        type: "FETCHING_METRIC_DATA",
        key: experimentKey
    }
}

function* downloadMetrics(src) {
    yield dispatch({
        type: "FETCH_METRIC_DATA",
        key: src,
    });
    // fixit: somehow this is called twice...
    const records = yield fileApi.getMetricData(src);
    yield dispatch({
        type: "SET_METRIC",
        key: src,
        records: records
    })
}

function undefinedOrDirty(record) {
    return (typeof record === 'undefined') || !!record.dirty;
}


export function* metricsDownloadProc() {
    /** fullKey should be of the form uriJoin(currentDirectory, path); */
    while (true) {
        const {state: {metricRecords}, action: {key}} = yield take('DIRTY');
        /* mark the metric as being downloaded */
        // console.log('detected dirty!!');
        if (undefinedOrDirty(metricRecords[key])) yield spawn(downloadMetrics, key);
    }
}

export function* metricsProc() {
    let state, action, metrics, metricRecords, currentDirectory;
    while (true) {
        ({state, action} = yield take('GO_TO'));
        let files;
        try {
            files = yield fileApi
                .getFiles(state.currentDirectory, "**/*[dr][ai][tc][as].pkl", 1, 100) //metrics and data.pkl.
            // .catch(yield ERROR_CALLBACK);
        } catch (e) {
            console.error(e);
        }
        ({state, action} = yield dispatch({
            type: "METRICS_ASSIGN",
            data: files
        }));
        ({state: {currentDirectory, metrics, metricRecords}, action} = yield dispatch({
            type: "METRICS_SORT",
            sortBy: "creation",
            order: -1
        }));
        yield dispatch({type: "UPDATE_SEARCH_RESULTS"})
        // for (let stat of metrics) {
        //     let fullKey = uriJoin(currentDirectory, stat.path);
        //     console.log(fullKey);
        //     // if (undefinedOrDirty(metricRecords[fullKey])) yield spawn(downloadMetrics, fullKey);
        // }
        // for (let stat of metrics) {
        //     let fullKey = uriJoin(currentDirectory, stat.path);
        //     if (undefinedOrDirty(metricRecords[fullKey]))
        //         yield spawn(downloadMetrics, fullKey);
        // }
    }
}

