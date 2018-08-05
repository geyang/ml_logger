import {take, dispatch, ERROR_CALLBACK, THEN_CALLBACK, spawn, delay, call, select} from 'luna-saga';
import {flattenParams, recordsToSeries} from "../data-helpers";
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
    if (!path) return;
    let slashInd = path.lastIndexOf('/');
    return path.slice(0, slashInd > -1 ? slashInd : 0);
}

//file api
export class FileApi {
    constructor(server = "") {
        this.configure(server);
        this.getFiles = this._getFiles.bind(this);
        this.getText = this._getText.bind(this);
        this.subscribeFileEvents = this._subscribeFileEvents.bind(this);
        this.getMetricData = this._getMetricData.bind(this);
        this.deletePath = this._deletePath.bind(this);
        this.batchGetPklAsJson = this._batchGetPklAsJson.bind(this);
        this.getPklAsJson = this._getPklAsJson.bind(this);
    }

    configure(server = "") {
        this.serverUri = server;
        this.batchFileEndpoint = `${this.serverUri}/batch-files`;
        this.fileEndpoint = `${this.serverUri}/files`;
        this.fileEvents = `${this.serverUri}/file-events`;
    }

    _getFiles(currentDirectory = "/", query = "", recursive = false, stop = 10, start = 0) {
        let uri = this.fileEndpoint + currentDirectory;
        const params = {};
        if (!!query) params.query = query;
        if (!!recursive) params.recursive = 1;
        if (!!start) params.start = start;
        if (!!stop) params.stop = stop;
        if (Object.keys(params).length) uri += `?${stringify(params)}`;
        return fetch(uri).then(status200).then(j => j.json())
    }

    _getText(fileKey = "/", query = "", stop, start) {
        // todo: start and stop are not being used
        let uri = this.fileEndpoint + fileKey;
        const params = {};
        if (!!query) params.query = query;
        if (start !== undefined) params.start = start;
        if (stop !== undefined) params.stop = stop;
        if (Object.keys(params).length) uri += `?${stringify(params)}`;
        return fetch(uri).then(status200).then(j => j.text())
    }

    _subscribeFileEvents(currentDirectory = "/", query = "") {
        let uri = this.fileEvents + currentDirectory;
        const params = {};
        if (!!query) params.query = query;
        if (!!params) uri += `?${stringify(params)}`;
        return fetch(uri).then(status200).then(j => j.json());
    }

    _getPklAsJson(path) {
        const src = this.fileEndpoint + path + "?json=1";
        return fetch(src, {headers: {'Content-Type': 'application/json; charset=utf-8'}})
            .then(status200)
            .then((r) => r.json())
        // .then((d) => recordsToSeries(d));
    }

    _batchGetPklAsJson(paths, options = {json: 1}) {
        const src = this.batchFileEndpoint;
        return fetch(src, {
            headers: {'Content-Type': 'application/json; charset=utf-8'},
            method: "POST",
            data: {paths, options}
        })
            .then(status200)
            .then((r) => r.json())
        // .then((d) => recordsToSeries(d));
    }

    _getMetricData(path) {
        const src = this.fileEndpoint + path + "?log=1";
        return fetch(src, {headers: {'Content-Type': 'application/json; charset=utf-8'}})
            .then(status200)
            .then((r) => r.json())
        // .then((d) => recordsToSeries(d));
    }

    _deletePath(path) {
        const src = this.fileEndpoint + path;
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
    return {type: 'QUERY_SET', value: query};
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

export const defaultState = {
    currentDirectory: "/",
    searchQuery: "",
    showComparison: false,
    showConfig: false,
};

const _fileReducer = combineReducers({
    searchQuery: ValueReducer('QUERY', ""),
    bucket: ValueReducer('BUCKET', ''),
    files: Files('FILES'),
    paramFiles: Files('PARAM_FILES'),
    metrics: Files('METRICS'),
    srcCache: CacheReducer('SRC'),
    filteredParamFiles: ValueReducer('FILTERED_PARAM_FILES', []),
    filteredFiles: ValueReducer('FILTERED_FILES', []),
    filteredMetricsFiles: ValueReducer('FILTERED_METRIC_FILES', []),
    chartKeys: ArrayReducer("CHARTKEYS", ["loss.*", ".*"]),
    parameterKeys: ArrayReducer("PARAMKEYS", []),
    // todo: absorb this into the chart definition, as part of chartConfig object.
    yMin: ValueReducer('Y_MIN', null),
    yMax: ValueReducer('Y_MAX', null),
});

export function BatchReducer(reducer, key = "BATCH_ACTIONS") {
    return function batchReducer(state, action) {
        if (action.type === key) for (let act of action.actions) {
            state = reducer(state, act)
        }
        return reducer(state, action);
    }
}

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

export function insertParamKey(ParamKey) {
    return {type: "PARAMKEYS_PUSH", item: ParamKey}
}

export function deleteParamKey(index) {
    return {type: "PARAMKEYS_DELETE", ind: index}
}

export function moveParamKey(index, newIndex) {
    return {type: "PARAMKEYS_MOVE", ind: index, newInd: newIndex}
}

export function setBucket(bucketKey) {
    return {type: "BUCKET_SET", value: bucketKey}
}

function fileReducer(state = defaultState, action) {
    if (action.type === "TOGGLE_COMPARISON") {
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
        return _fileReducer({
            ...state, currentDirectory,
            files: [], metrics: [], paramFiles: [],
            filteredFiles: [], filteredMetricsFiles: []
        }, action);
    }
    return _fileReducer(state, action);
}


export const rootReducer = BatchReducer(fileReducer, "BATCH_ACTIONS");

export function createBatchAction(...actions) {
    return {
        type: "BATCH_ACTIONS",
        actions
    }
}


export function* searchProc() {
    let state, action, searchQuery, currentDirectory, metrics, files, metricRecords, paramFiles, filteredMetrics;
    while (true) try {
        ({action} = yield take(/(UPDATE_SEARCH_RESULTS|QUERY_SET|FILES_SORT|METRIC_SORT)/));
        console.log('search process is started', action);
        if (!action.no_delay) yield call(delay, 200);
        ({searchQuery, currentDirectory, metrics, files, paramFiles, metricRecords, filteredMetrics} = yield select());
        yield dispatch({
            type: "BATCH_ACTIONS",
            actions: [
                {
                    type: "FILTERED_PARAM_FILES_SET",
                    value: paramFiles.filter(f => uriJoin(currentDirectory, f.path).match(searchQuery))
                },
                {
                    type: "FILTERED_FILES_SET",
                    value: files.filter(f => uriJoin(currentDirectory, f.path).match(searchQuery))
                },
                {
                    type: "FILTERED_METRIC_FILES_SET",
                    value: metrics.filter(f => uriJoin(currentDirectory, f.path).match(searchQuery))
                }

            ]
        });
        // const filteredMetrics = metrics.filter(f => metricRecords[f.path]
    } catch (e) {
        console.warn(e);
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

const apiRoot = "http://54.71.92.65:8082";
export const fileApi = new FileApi(apiRoot);

export function* locationProc() {
    let state, action;
    while (true) try {
        ({state, action} = yield take(PUSH_LOCATION));
        console.log(action.location);
        //todo: need to parse the parameters from the location object.
        // yield dispatch(goTo())
    } catch (e) {
        console.warn(e)
    }
}

export function* removeProc() {
    let state, action, res;
    while (true) {
        ({state, action} = yield take("REMOVE_PATH"));
        res = yield fileApi.deletePath(action.path);
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
                .getFiles(state.currentDirectory, "*", false, 1000);
            // .catch(yield ERROR_CALLBACK);
            try {
                yield dispatch({
                    type: "BATCH_ACTIONS",
                    actions: [
                        {
                            type: "FILES_ASSIGN",
                            data: files
                        }, {
                            type: "FILES_SORT",
                            sortBy: "creation",
                            order: -1
                        }
                    ]
                });
            } catch (e) {
                console.warn(e)
            }
            yield dispatch({type: "UPDATE_SEARCH_RESULTS"})
        } catch (e) {
            console.error(e);
        }
    }
}

//this is only needed for the metrics data b/c we want to plot them over.
//might also need for text files.
function CacheReducer(key = "SRC") {
    return function metricReducer(state = {}, action) {
        if (action.type === `${key}_DATA_SET`) {
            state = {...state, [action.key]: {data: action.data}};
            return state
        } else if (action.type === `${key}_DATA_REMOVE`) {
            state = {...state};
            delete state[action.key];
            return state;
        } else if (action.type === `${key}_DATA_DIRTY`) {
            let record = state[action.key];
            return {...state, [action.key]: {...record, $dirty: true}}
        } else if (action.type === `${key}_DATA_FETCHING`) {
            let record = state[action.key];
            return {...state, [action.key]: {...record, $fetching: true}}
        }
        return state
    }
}

export function markDirty(experimentKey) {
    return {
        type: "SRC_DATA_DIRTY",
        key: experimentKey
    }
}

export function fetchData(src, force = false) {
    return {
        type: "SRC_DATA_FETCH@@",
        key: src,
        force
    }
}

export function markFetching(experimentKey) {
    return {
        type: "SRC_DATA_FETCHING",
        key: experimentKey
    }
}

const batch_action_buffer = [];


function* downloadData(src) {
    let data = yield fileApi.getMetricData(src);
    if (src.match(/parameters.pkl/)) {
        data = flattenParams(data);
    }
    batch_action_buffer.push({
        type: "SRC_DATA_SET",
        key: src,
        data
    });
    let mem_length = batch_action_buffer.length;
    console.log('add action but not dispatching it.');
    if (batch_action_buffer.length >= 100) {
        console.log('buffer is full. Now dispatch throttled actions');
        let _ = createBatchAction(...batch_action_buffer);
        batch_action_buffer.length = 0;
        yield dispatch(_);
    } else {
        yield call(delay, 500);
        /* This makes sure that this is the last request.*/
        if (batch_action_buffer.length === mem_length) {
            console.log('dispatch throttled actions');
            let _ = createBatchAction(...batch_action_buffer);
            batch_action_buffer.length = 0;
            yield dispatch(_);
        }
    }
}


function notFetchingDirtyOrUndefined(data) {
    return (data === undefined || data === null) || !!data.$dirty && !data.$fetching;
}


export function* DownloadProc() {
    /** fullKey should be of the form uriJoin(currentDirectory, path); */
    while (true) try {
        const {state: {srcCache}, action: {key, force}} = yield take('SRC_DATA_FETCH@@');
        // console.log(key, metricRecords[key]);
        /* mark the metric as being downloaded */
        // console.log('detected dirty!!');
        if (force || notFetchingDirtyOrUndefined(srcCache[key])) {
            // todo: it is a bit annoying that this updates the store and triggers a rerendering
            yield dispatch(markFetching(key));
            yield spawn(downloadData, key);
        }
    } catch (e) {
        console.warn(e);
    }
}

export function* paramsProc() {
    let state, action;
    while (true) {
        ({state, action} = yield take('GO_TO'));
        let files;
        try {
            files = yield call(fileApi.getFiles, state.currentDirectory, "**/parameters.pkl", 1, 10000); //metrics and data.pkl.
            try {
                yield dispatch({
                    type: "BATCH_ACTIONS",
                    actions: [
                        {
                            type: "PARAM_FILES_ASSIGN",
                            data: files
                        }, {
                            type: "PARAM_FILES_SORT",
                            sortBy: "creation",
                            order: -1
                        }
                    ]
                });
            } catch (e) {
                console.error(e);
            }
            yield dispatch({type: "UPDATE_SEARCH_RESULTS"})
        } catch (e) {
            console.error(e);
        }
    }
}

