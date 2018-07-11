//@flow
/** Created by ge on 12/26/17. */
import {Store} from "luna";
import {sagaConnect, call, fork, spawn, take, dispatch, delay, select, SAGA_CONNECT_ACTION} from "luna-saga";
import type {TRichResult, TSimpleResult} from "./types";
import {googleAutoComplete} from "./helpers";

type TSearchStore = {
    query: string,
    autoComplete: {
        selection: number,
        results: Array<TSimpleResult>
    },
    selection: number,
    results: Array<TSimpleResult | TRichResult>
}

const InitState: TSearchStore = {
    query: "",
    autoComplete: {selection: -1, results: []},
    selection: -1,
    results: []
};

type TAction = { type: string };
type TSearchCallbackAction = TAction & { items: Array<TSimpleResult | TRichResult> }

const $SymNameSpace = (namespace) => (key) => `${namespace}_${key}`;
const $ = $SymNameSpace('SEARCH');

const search = function (state: TSearchStore = InitState, action: TSearchCallbackAction) {
    if (action.type === $("INPUT")) {
        return {...state, query: action.query};
    } else if (action.type === $("COMPLETE_CB")) {
        // todo: maintain identity of selected item
        return {...state, autoComplete: {selection: -1, results: action.items}};
    } else if (action.type === $("SEARCH_CB")) {
        return {...state, selection: -1, results: action.items};
    } else {
        return state;
    }
};

export function* Search(): Generator<any, any, any> {
    const newState: any = yield select();
    const {items} = yield googleAutoComplete({text: newState.query});
    yield dispatch({type: $("COMPLETE_CB"), items});
}

// todo: make a throttling process

const rising = true;
const falling = true;
const interval = 300;
const asyncFn = (cb?: Function) => {
    const p = new Promise((res, rej) => setTimeout(res(10), 10000));
    p.then(cb);
};
const triggerAction = $("INPUT");

export function* throttle(name = "throttle"): Generator<any, any, any> {
    let proc;
    while (true) try {
        const {state} = yield take(triggerAction);
        console.log(`0 ========${name}=========`);
        // if (rising) proc = yield spawn(asyncFn, (n) => console.log(`callback ${name}: ${n}`));
        // console.log(`1 ========${name}=========`);
        // const {state: newState} = yield take(triggerAction);
        console.log(`2 ========${name}=========`);
        yield call(delay, interval);
        console.log(`3 ========${name}=========`);
        // if (state != newState && !!falling) proc = yield spawn(asyncFn);
        // console.log(`4 ========${name}=========`);
    } catch (e) {
        console.error("throttle process", e);
    }
}

export function* SearchProcess() {
    let proc;
    while (true) try {
        const {state, _} = yield take($("INPUT"));
        proc = yield spawn(Search);
        yield call(delay, 300);
        const newState = yield select(/* selector for the search store. */);
        if (newState !== state && !proc.isStopped) {
            proc.complete(); // just terminate that process.
            proc = yield spawn(Search)
        }
    } catch (e) {
        console.error(e)
    }
}

const store$ = new Store(search);
// store$.update$.subscribe(({state, action}) => console.log(state, action), (err) => console.warn(err), () => console.log("*** completed ***"));
const proc = sagaConnect(store$, SearchProcess());
// const proc_2 = sagaConnect(store$, throttle("throttle_TWO"));
// proc.subscribe({error: (err) => console.warn(err)});

function put(a) {
    store$.dispatch(a);
}

put({type: $("INPUT"), query: "A"});
put({type: $("INPUT"), query: "An"});
put({type: $("INPUT"), query: "And"});
put({type: $("INPUT"), query: "Andr"});
put({type: "NOOP"});
put({type: "NOOP"});
put({type: "NOOP"});
put({type: "NOOP"});
put({type: "LATER"});
put({type: "NOOP"});
put({type: "NOOP"});
let i = 0;
while (i < 1000000) {
    i += 1;
    put({type: $("INPUT"), query: "A"});
    put({type: $("INPUT"), query: "An"});
    put({type: $("INPUT"), query: "And"});
    put({type: $("INPUT"), query: "Andr"});
    // console.log(i);
}
