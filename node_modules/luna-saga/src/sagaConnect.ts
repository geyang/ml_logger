import {Store, Thunk, Action, StateActionBundle} from "luna";
import Saga, {SAGA_CONNECT_ACTION} from "./Saga";

export function sagaConnect<TState>(store$: Store<TState>,
                                    iterator: Iterator<any>,
                                    immediate: boolean = true): Saga<TState> {
    let process = new Saga<TState>(iterator);

    // update$ is a Subject, so no value can be obtained before the first update happens. This
    // is causing problems to the select effect.

    // connect the process to the update bundle stream of the store.
    // This subscription should be destroyed when process finishes.
    // store$.update$.takeUntil(process.term$).subscribe(process);
    process.subscribeTo(store$.update$);
    // connect the action$ and thunk$ stream to the main store.
    // These streams will complete on process termination
    // since dispatch is just a function, store$ won't be affected (completed).
    // store is usually long-lived, so we don't need to use take until.
    // these streams are just notifying the dispatch function.
    process.thunk$.subscribe(store$.dispatch);
    process.action$.subscribe(store$.dispatch);

    if (immediate) {
        process.run();
        // right after run, emit a special connect action, which transmits
        // the state value, to allow `select` and other effects to `take`
        // the state right away.
        let initialUpdate = {
            state: store$.getValue(),
            action: {type: SAGA_CONNECT_ACTION}
        } as StateActionBundle<TState>;

        process.next(initialUpdate);
    }
    // if manually run, then the user would need to manually emit the connect action.
    return process;
}
