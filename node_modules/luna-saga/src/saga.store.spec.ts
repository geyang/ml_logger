/** Created by ge on 3/27/16. */
/* so that this show up as a module */
import Saga from "./Saga";
export default {};

/** Created by ge on 12/6/15. */
import {Action, Hash, Reducer, Store, INIT_STORE_ACTION} from "luna";
import {Thunk} from "luna/dist/index";
import {isAction} from "./util/isAction";

interface TestAction extends Action {
    payload?: any;
}
interface TState {
    counter: number;
    name: string;
}

describe("saga.store.spec: store thread schedule", function () {
    it("the dispatch calls should run in a different thread", function (done: () => void) {
        let counterReducer = <Reducer>function <Number>(state: number = 0, action: TestAction): number {
            if (action.type === "INC") {
                return state + 1;
            } else if (action.type === "DEC") {
                return state - 1;
            } else {
                return state;
            }
        };
        let stringReducer = <Reducer>function <String>(state: string = "", action: TestAction): string {
            if (action.type === "SET") {
                return action.payload;
            } else if (action.type === "CAPITALIZE") {
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

        let validThunk_has_ran = false;

        function validThunk(): any {
            validThunk_has_ran = true;
            return {type: "VALID_ACTION_STUB"};
        }

        let nullThunk_has_ran = false;

        function nullThunk(): null {
            nullThunk_has_ran = true;
            return null;
        }

        function* proc(): Iterator<any> {
            console.log('process should');
            yield {type: 'INC'};

            // you can yield thunk, but thunks are not executed unless
            // there is a store with `store.dispatch` method.
            // In this case, this thunk would execute.
            let result = yield validThunk;
            expect(result).toBe(validThunk);
            expect(validThunk_has_ran).toBe(true);

            // falsy value from a thunk should not enter the action$ downstream
            result = yield nullThunk;
            expect(result).toBe(nullThunk);
            expect(nullThunk_has_ran).toBe(true);

            yield done;
        }

        let saga$ = new Saga<TState>(proc());
        let store$ = new Store<TState>(rootReducer); // does not need to pass in  a initial state

        //store$.map(state => ({state, "action": store$.action$.getValue()})).subscribe(_=> console.log("stream:", _));
        saga$.action$.subscribe((action: TestAction) => store$.dispatch(action));
        saga$.thunk$.subscribe((thunk: Thunk) => store$.dispatch(thunk));

        store$.action$.subscribe(action => {
            if (!isAction(action))
                throw Error('ill-formed action is passed through.' + JSON.stringify((action)));
            else console.log("store$.action$ >> ", action)
        });
        saga$.run()
    });
});

