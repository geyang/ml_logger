/** Created by ge on 12/17/15. */
import {Reducer, Hash} from "./interfaces";
import {Store} from "./Store";
export function createStore <TState>(reducer:Reducer|Hash<Reducer>, initialState:TState):any {
    return () => {
        return new Store(reducer, initialState);
    };
}
