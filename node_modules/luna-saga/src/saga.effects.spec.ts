/** Created by ge on 3/27/16. */
import Saga, {CHILD_ERROR} from "./Saga";
import {Action} from "luna";
import {take, dispatch, call, apply, select, fork, spawn} from "./effects/effectsHelpers";
import {Store} from "luna/dist/index";
import {Reducer} from "luna/dist/index";
import {delay, throttle} from "./helpers";
import {SAGA_CONNECT_ACTION} from "./Saga";
import {isAction} from "./util/isAction";

interface TestState {
    number?: number;
}

interface TestAction extends Action {
    payload?: any;
}

describe("saga.effects.spec", function () {
    jasmine.DEFAULT_TIMEOUT_INTERVAL = 4000;
    it("take effect allow yield on a certain type of actions", function (done: () => void) {

        function* idMaker(): Iterator<any> {
            let update: any;
            update = yield take(/I(.*)STORE$/);
            console.log('0 *****', update);
            expect(update).toEqual({state: {number: 0}, action: {type: "INIT_STORE"}});
            update = yield take("INC");
            console.log('1 *****', update);
            expect(update).toEqual({state: {number: 1}, action: {type: "INC"}});
            // can test NOOP actions without getting hangup
            update = yield dispatch({type: "NOOP"});
            console.log('2 *****', update);
            update = yield dispatch({type: "NOOP"});
            console.log('2.5 *****', update);
            expect(update).toEqual({state: {number: 1}, action: {type: "NOOP"}});
            update = yield call(() => "returned value");
            console.log('3 *****', update);
            // now delay:
            yield call(delay, 500);
            expect(update).toEqual("returned value");
            update = yield call([{color: "red"}, function (flower: any) {
                return `${flower} is ${this.color}`
            }], "rose");
            expect(update).toBe('rose is red');
            update = yield apply({color: "blue"}, function (thing: any) {
                return `${thing} is ${this.color}`
            }, "sky");
            expect(update).toBe('sky is blue');
            let state: any;
            state = yield select();
            expect(state).toEqual({number: 1});
            state = yield select("number");
            expect(state).toBe(1);
            yield done;
        }

        let saga = new Saga<TestState>(idMaker());
        let testActions = [
            {type: "INIT_STORE"},
            {type: "INC"},
            {type: "random"},
            {type: "another random action"},
            {type: "NOOP"}
        ];
        // building the test store
        let counterReducer = <Reducer>function <Number>(state: number = 0, action: TestAction): number {
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
        saga.subscribeTo(store$.update$);
        saga.action$.subscribe((action: any) => {
            console.log("action: ", action);
            if (!isAction(action)) throw console.error("action is ill defined", action);
            store$.dispatch(action);
        });
        saga.thunk$.subscribe((_: any) => {
            console.log("thunk: ", _);
            store$.dispatch(_);
        });
        saga.log$.subscribe((_: any) => console.log("log$: ", _));
        store$.update$.subscribe((_: any) => console.log("udpate$: ", _));
        saga.subscribe({error: (err: any) => console.log("saga error: ", err)});
        /* run saga before subscription to states$ in this synchronous case. */
        saga.run();

        function run(action: any) {
            store$.dispatch(action);
            console.log(`dispatch(${action})`);
        }

        run(testActions[0]);
        run(testActions[1]);
        run(testActions[2]);
        run(testActions[3]);
        run(testActions[4]);
    });

    it("test select effect corner cases", function (done: () => void) {

        function* idMaker(): Iterator<any> {
            let numberState: any;
            // as long as a synthesized SAGA_CONNECT event is emitted with state value
            // the select effect would have the state already populated in the replay
            // subject. [^reference](./sagaConnect.ts:L19)
            numberState = yield select("number");
            console.log('4 *****', numberState);
            expect(numberState).toEqual(0);
            numberState = yield select("number");
            console.log('5 *****', numberState);
            expect(numberState).toEqual(0);
            numberState = yield select("number");
            console.log('6 *****', numberState);
            expect(numberState).toEqual(0);
            yield done;
        }

        let saga = new Saga<TestState>(idMaker());

        // building the test store
        let counterReducer = <Reducer>function <Number>(state: number = 0, action: TestAction): number {
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
        saga.action$.subscribe((action: any) => {
            console.log("action: ", action);
            if (!isAction(action)) throw console.error("action is ill defined", action);
            store$.dispatch(action);
        });
        saga.thunk$.subscribe((_: any) => {
            console.log("thunk: ", _);
            store$.dispatch(_);
        });
        saga.log$.subscribe((_: any) => console.log("log: ", _));
        saga.subscribe({error: (err: any) => console.log("saga error: ", err)});
        /* run saga before subscription to states$ in this synchronous case. */
        saga.run();
        saga.next({state: store$.getValue(), action: {type: <string>SAGA_CONNECT_ACTION}});

    });

    it("generator handling with CALL effect handler", function (done: () => void) {

        function* oneTimeGenerator(): Iterator<any> {
            console.log('executing oneTimeGenerator');
            console.log("call result",
                yield call((_: any) => console.log('inside called function >>> args=', _), "input argument"));
            console.log("call result",
                yield call(delay, 100));
            yield call(() => console.log('oneTimeGenerator has finished running'));
        }

        function* processStub(): Iterator<any> {
            console.log("test delay >> ", yield call(delay, 100));
            yield call(oneTimeGenerator);
            console.log('processStub has finished running');
            // delay to make sure that this process terminate after oneTimeGenerator.
            yield call(delay, 200);
        }

        let saga = new Saga<TestAction>(processStub());
        let startDate = Date.now();
        saga.subscribe({error: (err: any) => console.log("saga error: ", err)});
        saga.log$.subscribe(console.log, null, () => {
                console.log(`saga execution took ${(Date.now() - startDate) / 1000} seconds`);
                done()
            }
        );
        saga.run();
    });

    it('fork example', function (done: () => void) {
        function* main() {
            yield fork(sub);
            yield call(delay, 100);
            yield "main-routing";
            /* make sure that the parent ends after the child. */
            // todo: keep parent alive when child is still running.
            yield call(delay, 150);
            yield "main-routing end";
        }

        const errorStub = new Error('errorStub, should error out b/c throw is un-catched inside generator.');

        function* sub() {
            console.log("sub-routine: 0");
            yield call(delay, 100);
            console.log("sub-routine: delayed");
            yield call(delay, 100);
            /* the sub routine should be able to finish execution. */
            console.log("sub-routine: throw");
            throw errorStub;
            // console.log("sub-routine: end << should never hit here.");
        }

        let saga = new Saga<TestAction>(main());
        saga.log$.subscribe(null, console.error);
        saga.subscribe({
            error: (err) => {
                expect(err.type).toBe(CHILD_ERROR);
                expect(err.err).toBe(errorStub);
                done();
            }
        });
        saga.run();
    });


    it('spawn example', function (done: () => void) {
        function* main() {
            yield spawn(sub);
            yield call(delay, 100);
            yield "main-routing";
            /* make sure that the parent ends after the child. */
            // todo: keep parent alive when child is still running.
            yield call(delay, 500);
            yield "main-routing end";
        }

        const errorStub = new Error('hahaha');

        function* sub() {
            console.log("sub-routine: 0");
            yield call(delay, 100);
            console.log("sub-routine: end");
            yield call(delay, 100);
            throw errorStub;
            /* the sub routine should be able to finish execution. */
        }

        let saga = new Saga<TestAction>(main());
        saga.log$.subscribe(null, console.error);
        saga.subscribe({
            error: (err) => {
                expect(err).not.toBeDefined(err);
            }
        });
        saga.subscribe(null, null, () => done());

        saga.run();
    });

    it('throttle example', function (done: () => void) {
        let id;

        function asyncFunc() {
            setTimeout(() => {
                id += 1;
            }, 5);
        }

        function* runner() {
            id = 0;
            let proc = new Saga(throttle(asyncFunc, "TRIG", 300, true));
            proc.run();
            proc.next({state: {}, action: {type: "TRIG"}});
            yield call(delay, 100);
            expect(id).toBe(1);
            proc.next({state: {}, action: {type: "TRIG"}});
            yield call(delay, 100);
            expect(id).toBe(1);
            yield call(delay, 110); // 305 ms point.
            expect(id).toBe(2);
            proc.complete();

            id = 0;
            proc = new Saga(throttle(asyncFunc, "TRIG", 200, false));
            proc.run();
            proc.next({state: {}, action: {type: "TRIG"}});
            yield call(delay, 50);
            expect(id).toBe(1);
            proc.next({state: {}, action: {type: "TRIG"}});
            yield call(delay, 160); // 210 ms point
            expect(id).toBe(1);

            // new cycle
            proc.next({state: {}, action: {type: "TRIG"}});
            expect(id).toBe(1);
            yield call(delay, 15);
            expect(id).toBe(2);

            proc.complete();
            done();
        }

        let p = new Saga(runner());
        p.run()
    })
});


