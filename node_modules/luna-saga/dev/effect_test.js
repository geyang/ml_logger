import Saga, {take, dispatch, call, delay, apply, select} from "../dist";
import {isAction} from "../dist/util/isAction";
import {Store} from "luna";
import "should";

function* idMaker(): Iterator<any> {
    let update: any;
    update = yield take(/I(.*)STORE$/);
    should(update).be.eql({state: {number: 0}, action: {type: "INIT_STORE"}});
    update = yield take("INC");
    should(update).be.eql({state: {number: 1}, action: {type: "INC"}});
    update = yield dispatch({type: "NOOP"});
    should(update).be.eql({state: {number: 1}, action: {type: "NOOP"}});
    update = yield dispatch({type: "NOOP"});
    should(update).be.eql({state: {number: 1}, action: {type: "NOOP"}});
    update = yield call(() => "returned value");
    // now delay:
    yield call(delay, 500);
    should(update).be.eql("returned value");
    update = yield call([{color: "red"}, function (flower: any) {
        return `${flower} is ${this.color}`
    }], "rose");
    should(update).be.equal('rose is red');
    update = yield apply({color: "blue"}, function (thing: any) {
        return `${thing} is ${this.color}`
    }, "sky");
    should(update).be.equal('sky is blue');
    let state: any;
    state = yield select();
    should(state).be.eql({number: 1});
    state = yield select("number");
    should(state).be.equal(1);
    console.log('FINISHED!')
}

let saga = new Saga(idMaker());
let testActions = [
    {type: "INIT_STORE"},
    {type: "INC"},
    {type: "random"},
    {type: "another random action"},
    {type: "NOOP"}
];
// building the test store
let counterReducer = function (state: number = 0, action): number {
    if (action.type === "INC") {
        return state + 1;
    } else if (action.type === "DEC") {
        return state - 1;
    } else {
        return state;
    }
};
let store$ = new Store({number: counterReducer});
// subscribe the saga to the store (state,action) bundle
store$.update$.subscribe(saga);
store$.update$.subscribe(({state, action}) => console.log("update$.subscription.action", action));
store$.subscribe((state) => console.log('===> state: ', state));
saga.subscribe(({state, action}) => console.log('(saga.subscription).action', action));
saga.replay$.subscribe(({state, action}) => console.log('(saga.replay$.subscription).action', action));
saga.action$.subscribe((action: any) => {
    console.log("action: ", action);
    if (!isAction(action)) throw console.error("action is ill defined", action);
    store$.dispatch(action);
});
saga.thunk$.subscribe((_: any) => {
    console.log("thunk: ", _);
    store$.dispatch(_);
});
saga.log$.subscribe((_: any) => console.log("log: ".green, _));
saga.subscribe({error: (err: any) => console.log("saga error: ", err)});
/* run saga before subscription to states$ in this synchronous case. */
saga.run();

let i = 0;

function _dispatch(action) {
    console.log('$dispatching action', action);
    // store$.dispatch(action);
    setTimeout(() => store$.dispatch(action), 100 * i);
    i += 1;
}

_dispatch(testActions[0]);
_dispatch(testActions[1]);
_dispatch(testActions[2]);
_dispatch(testActions[3]);
_dispatch(testActions[4]);
_dispatch(testActions[4]);
