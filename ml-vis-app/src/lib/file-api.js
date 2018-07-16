import {take, dispatch, ERROR_CALLBACK, THEN_CALLBACK} from 'luna-saga';
import {recordsToSeries} from "../data-helpers";
import {stringify} from "query-string";
import {status200} from "./fetch-helper";
import {PUSH_LOCATION} from "./routeStoreConnect";
import {combineReducers} from "luna";

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
        const src = uriJoin(this.fileEndpoint, path);
        console.log(src);
        return fetch(src, {headers: {'Content-Type': 'application/json; charset=utf-8'}})
            .then(status200)
            .then((r) => r.json())
            .then((d) => recordsToSeries(d));
    }

    deletePath(path) {
        const src = uriJoin(this.fileEndpoint, path);
        console.log(src);
        return fetch(src, {method: "DELETE",}).then(status200)
    }
}

export const defaultFileState = {
    currentDirectory: "/",
    searchQuery: ""
};

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
            if (action.sortBy === "time") {
                files = files.sort((a, b) => a.mime > b.mime)
            } else if (action.sortBy === "prefix") {
                files = files.sort((a, b) => a.name > b.name)
            } else if (action.sortBy === "postfix") {
                files = files.sort((a, b) =>
                    a.name.split('').reverse().join('') > b.name.split('').reverse().join(''))
            }
            if (action.order = -1) {
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
});

function fileReducer(state = defaultFileState, action) {
    if (action.type === "SET_QUERY") {
        return {...state, searchQuery: action.query};
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
        console.log(state);
        state = _fileReducer({...state, currentDirectory}, action);
        console.log(state);
        return state
    }
    return _fileReducer(state, action);
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
        console.log('111111111111111111111111111111111');
        ({state, action} = yield take("REMOVE_PATH"));
        console.log('222222222222222222222222222222222');
        console.log(action.path);
        res = yield fileApi.deletePath(action.path);
        console.log(res);
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
            sortBy: "prefix",
            order: -1
        }));
    }
}

export function* metricsProc() {
    let state, action;
    while (true) {
        ({state, action} = yield take('GO_TO'));
        let files;
        try {
            files = yield fileApi
                .getFiles(state.currentDirectory, "**/*[dt][ai][tc][as].pkl", 1, 20) //metrics and data.pkl.
            // .catch(yield ERROR_CALLBACK);
        } catch (e) {
            console.error(e);
        }
        ({state, action} = yield dispatch({
            type: "METRICS_ASSIGN",
            data: files
        }));
        ({state, action} = yield dispatch({
            type: "METRICS_SORT",
            sortBy: "prefix",
            order: -1
        }));
    }
}
