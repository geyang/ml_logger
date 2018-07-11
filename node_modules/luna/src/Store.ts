/** Created by ge on 12/4/15. */
import {BehaviorSubject, Subject, Observable} from 'rxjs';
import {passOrCombineReducers} from './util/combineReducers';
import {Action, Thunk, Reducer, Hash, StateActionBundle} from "./interfaces";
import {isAction} from "./util/isAction";

export const INIT_STORE = '@@luna/INIT_STORE';
export const INIT_STORE_ACTION = {type: INIT_STORE};

export class Store<TState> extends BehaviorSubject<TState> {
    public rootReducer: Reducer;
    public dispatch: (action: Action|Thunk) => void;
    public update$: Subject<StateActionBundle<TState>>;
    public action$: Subject<Action>;

    constructor(rootReducer: Reducer | Hash<Reducer>,
                initialState?: TState) {
        // this is a stream for the states of the store, call BehaviorSubject constructor
        super(passOrCombineReducers(rootReducer)(initialState, INIT_STORE_ACTION));
        this.dispatch = this._dispatch.bind(this);
        this.rootReducer = passOrCombineReducers(rootReducer);

        // action$ is a stream for action objects
        this.action$ = new Subject<Action>();
        this.update$ = new Subject<StateActionBundle<TState>>();
        this.action$
            .subscribe(
                (action) => {
                    let currentState: TState = this.getValue();
                    let newState: TState = this.rootReducer(currentState, action);
                    this.next(newState);
                    this.update$.next({state: newState, action})
                },
                (error) => console.log('dispatcher$ Error: ', error.toString()),
                () => console.log('dispatcher$ completed')
            );

        this.action$.next(INIT_STORE_ACTION);
    }

    _dispatch(action: Action|Thunk) {
        let _action: Action,
            _actionThunk: Thunk,
            newAction: Action;
        if (typeof action === 'function') {
            _actionThunk = action as Thunk;
            newAction = <Action>_actionThunk.apply(this);
            if (isAction(newAction)) return this.action$.next(newAction);
        } else if (!isAction(action)) {
            console.error("action object ill-defined: ", action, "will not pass in.");
        } else {
            _action = action as Action;
            this.action$.next(_action);
        }
    }

    // this method is just a wrapper function to make it compatible with redux convention.
    getState(): TState {
        return this.getValue();
    }

    select <TRState>(key: string): Observable<TRState> {
        return this
            .map((state: any) => {
                var rState: TRState = state[key] as TRState;
                return rState;
            })
            .distinctUntilChanged();
    }

    destroy = () => {
        this.action$.complete();
        this.complete();
    }
}
