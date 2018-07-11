/** Created by ge on 3/26/16. */

/* so that this show up as a module */
import {isAction} from "./util/isAction";
export default {};
/** Created by ge on 12/6/15. */
import {Action, Hash, Reducer} from "./index";

// the Stat interface need to extend Hash so that the index keys are available.

let reducer = <Reducer>function (state: number = 0, action: Action, callback: (state: number) => void): number {
    if (action.type === "INC") {
        return state + 1;
    } else if (action.type === "DEC") {
        return state - 1;
    } else if (action.type === "ASYNC_INC") {
        setTimeout(() => {
            callback(state + 1);
        }, 10);
        return undefined;
    } else if (action.type === "ASYNC_DEC") {
        setTimeout(() => {
            callback(state - 1);
        }, 10);
        return undefined;
    } else {
        return state;
    }
};

describe("interfaces", function () {
    it("Reducer can be a function", function () {
        let state: number = undefined;
        state = reducer(state, {type: "INC"});
        expect(state).toBe(1);
        state = reducer(state, {type: "DEC"});
        expect(state).toBe(0);
    });
    it("reducer should contain initial state", function () {
        let state: number;
        expect(state).toBeUndefined();
        state = reducer(state, {type: "INC"});
        expect(state).toBe(1);
        state = reducer(state, {type: "DEC"});
        expect(state).toBe(0);
    });
});

import {Store} from "./index";
describe("store", function () {
    it("should contain action$ and update$ stream", function () {
        let state: number = 10;
        let store = new Store<number>(reducer, state);
        // store should contain action$ and update$ stream.
        expect(store.action$).toBeDefined();
        expect(store.update$).toBeDefined();
    });
    it("sync reducers should work", function () {
        let state: number = 10;
        let store = new Store<number>(reducer, state);

        store.subscribe(
            (state) => {
                console.log('spec state: ', state)
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch({type: "INC"});
        expect(store.value).toEqual(11);
        store.dispatch({type: "DEC"});
        expect(store.value).toEqual(10);
        store.destroy();
    });
});
describe("dispatch function", function () {

    it("support action creator", function () {
        let state: number = 30;
        let store = new Store<number>(reducer, state);

        function increase(): Action {
            return {
                type: "INC"
            };
        }

        store.subscribe(
            (state) => {
                console.log('spec state: ', state)
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch(increase());
        store.dispatch({type: "DEC"});
        store.destroy();
    });
    it("support thunk; properly handle null or undefined actions from thunk.", function () {
        let state: number = 40;
        let store = new Store<number>(reducer, state);

        function increase(): Action {
            return {
                type: "INC"
            };
        }

        store.subscribe(
            (state) => {
                console.log('spec state: ', state)
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );

        store.update$.subscribe(
            ({state, action}) => {
                if (!isAction(action)) throw Error("ill-formed action is allowed to get dispatched");
            }
        );
        // null or undefined results from thunk should not be passed through by dispatch
        store.dispatch(() => null);
        store.dispatch(() => undefined);

        // dispatching typical thunks
        store.dispatch(increase);
        store.dispatch({type: "DEC"});
        store.destroy();
    });
    it("thunk have access to dispatch", function () {
        let state: number = 40;
        let store = new Store<number>(reducer, state);

        function increase(): void {
            let _store: Store<number> = this;
            setTimeout(function (): void {
                let action: Action = {
                    type: "INC"
                };
                _store.dispatch(action)
            }, 200);
        }

        store.subscribe(
            (state) => {
                console.log('spec state: ', state)
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch(increase);
        store.dispatch({type: "DEC"});
        setTimeout(() => {
            store.destroy();
        }, 210)
    })

});
describe("store with hash type", function () {
    it("can accept actions without initial state (an properly handle the initialization)", function () {
        interface TState extends Hash<number> {
        }

        let reducer = <Reducer>function <Number>(state: number = 0, action: Action): number {
            if (action.type === "INC") {
                return state + 1;
            } else if (action.type === "DEC") {
                return state - 1;
            } else {
                return state;
            }
        };
        let rootReducer: Hash<Reducer> = {
            counter: reducer
        };

        let store = new Store<TState>(rootReducer);

        function increase(): void {
            let _store: Store<TState> = this;
            setTimeout(function (): void {
                let action: Action = {
                    type: "INC"
                };
                _store.dispatch(action);
            }, 200);
        }

        store.subscribe(
            (state) => {
                console.log('spec state: ', state);
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch(increase);
        store.dispatch({type: "DEC"});
        setTimeout(() => {
            store.destroy();
        }, 210)
    });
    it("can take initial value", function () {
        interface TState extends Hash<number> {
        }
        let state: TState = {
            counter: 40
        };

        let reducer = <Reducer>function <Number>(state: number = 0, action: Action): number {
            if (action.type === "INC") {
                return state + 1;
            } else if (action.type === "DEC") {
                return state - 1;
            } else {
                return state;
            }
        };
        let rootReducer: Hash<Reducer> = {
            counter: reducer
        };

        let store = new Store<TState>(rootReducer, state);

        function increase(): void {
            let _store: Store<TState> = this;
            setTimeout(function (): void {
                let action: Action = {
                    type: "INC"
                };
                _store.dispatch(action);
            }, 200);
        }

        store.subscribe(
            (state) => {
                console.log('spec state: ', state);
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch(increase);
        store.dispatch({type: "DEC"});
        setTimeout(() => {
            store.destroy();
        }, 210);
    });
    it("accept reducers of different types", function () {
        interface TState {
            counter: number;
            name: string;
        }
        let state: TState = {
            counter: 40,
            name: 'Captain Kirk'
        };

        let counterReducer = <Reducer>function <Number>(state: number, action: Action): number {
            if (action.type === "INC") {
                return state + 1;
            } else if (action.type === "DEC") {
                return state - 1;
            } else {
                return state;
            }
        };
        let stringReducer = <Reducer>function <String>(state: string, action: Action): string {
            if (action.type === "CAPITALIZE") {
                return state.toUpperCase();
            } else if (action.type === "LOWERING") {
                return state.toLowerCase();
            } else {
                return state;
            }
        };
        let rootReducer: Hash<Reducer> = {
            counter: counterReducer,
            name: stringReducer
        };

        let store = new Store<TState>(rootReducer, state);

        store.subscribe(
            (state) => {
                console.log('spec state: ', state)
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch({type: "CAPITALIZE"});
        store.dispatch({type: "LOWERING"});
        store.dispatch({type: "INC"});
        store.destroy();
    });
    it("should allow filtered partial states in a stream", function () {
        interface TState {
            counter: number;
            name: string;
        }
        let state: TState = {
            counter: 40,
            name: 'Captain Kirk'
        };

        let counterReducer = <Reducer>function <Number>(state: number, action: Action): number {
            if (action.type === "INC") {
                return state + 1;
            } else if (action.type === "DEC") {
                return state - 1;
            } else {
                return state;
            }
        };
        let stringReducer = <Reducer>function <String>(state: string, action: Action): string {
            if (action.type === "CAPITALIZE") {
                return state.toUpperCase();
            } else if (action.type === "LOWERING") {
                return state.toLowerCase();
            } else {
                return state;
            }
        };
        let rootReducer: Hash<Reducer> = {
            counter: counterReducer,
            name: stringReducer
        };

        let store = new Store<TState>(rootReducer, state);

        store.select('name').subscribe(
            (state) => {
                console.log('spec state: ', state);
            },
            error => console.log('error ', error),
            () => console.log('completed.')
        );

        // mock persistent storage example
        store
            .select('counter')
            .subscribe((count: number): void => console.log('counter saving event: ', count));

        store.dispatch({type: "CAPITALIZE"});
        store.dispatch({type: "LOWERING"});
        store.dispatch({type: "INC"});
        store.dispatch({type: "DEC"});


        store.destroy();
    });

});