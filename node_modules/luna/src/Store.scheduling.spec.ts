/** Created by ge on 3/26/16. */
/* so that this show up as a module */
export default {};

/** Created by ge on 12/6/15. */
import {Action, Hash, Reducer, Store, INIT_STORE_ACTION} from "./index";

interface TestAction extends Action {
    payload?:any;
}
interface TState {
    counter: number;
    name: string;
}

describe("store thread schedule", function () {
    it("the dispatch calls should run in a different thread", function (done:()=>void) {
        let counterReducer = <Reducer>function <Number>(state:number = 0, action:TestAction):number {
            if (action.type === "INC") {
                return state + 1;
            } else if (action.type === "DEC") {
                return state - 1;
            } else {
                return state;
            }
        };
        let stringReducer = <Reducer>function <String>(state:string = "", action:TestAction):string {
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
        var rootReducer:Hash<Reducer> = {
            counter: counterReducer,
            name: stringReducer
        };

        var store = new Store<TState>(rootReducer); // does not need to pass in  a inital state
        // you can not capture the INIT_STORE action,
        // because the <store>.action$ stream is HOT
        // and the initialization happens synchronously.
        expect(store.value).toEqual({counter: 0, name: ""});

        store.subscribe(
            (state)=> {
                console.log('spec state: ', state)
            },
            error=> console.log('error ', error),
            () => console.log('completed.')
        );
        store.dispatch({type: "SET", payload: "episodeyang"});
        expect(store.value).toEqual({counter: 0, name: "episodeyang"});
        store.dispatch({type: "CAPITALIZE"});
        expect(store.value).toEqual({counter: 0, name: "EPISODEYANG"});
        store.dispatch({type: "LOWERING"});
        expect(store.value).toEqual({counter: 0, name: "episodeyang"});
        store.dispatch({type: "INC"});
        expect(store.value).toEqual({counter: 1, name: "episodeyang"});

        /*Now let's do something complicated*/
        var subscription = store.select('counter').subscribe(count=> store.dispatch({type: "CAPITALIZE"}));
        store.dispatch({type: "INC"});
        expect(store.value).toEqual({counter: 2, name: "EPISODEYANG"});
        subscription.unsubscribe();

        /* an anti-pattern */
        var subscription = store.select('name')
            .subscribe(name=> {
                store.dispatch({type: "INC"})
            });
        store.dispatch({type: "SET", payload: "Ge Yang"});
        /* the counter increase fires twice, once on subscription, once on update because
         * the store is a behavioralSubject. It is equivalent to ReplaySubject with a buffer
          * size of 2 in this regard.
          * If you want to avoid triggering on subscription, use update$ or action$ */
        expect(store.value).toEqual({counter: 4, name: "Ge Yang"});
        subscription.unsubscribe();

        /* Now let's add some async subscription */
        var subscription = store.select('name').subscribe(name=> {
            setTimeout(()=> {
                var currentCount = store.value.counter;
                store.dispatch({type: "INC"});
                expect(store.value.counter).toBe(currentCount + 1);
            }, 10);
        });
        store.dispatch({type: "CAPITALIZE"});
        expect(store.value).toEqual({counter: 4, name: "GE YANG"});
        setTimeout(()=> {
            expect(store.value).toEqual({counter: 6, name: "GE YANG"});
            subscription.unsubscribe();
            store.destroy();
            done()
        }, 100);
    });
});
