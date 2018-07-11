import {Action, Hash, Reducer} from "../interfaces";
// helper function
function pickReducers<Reducer>(reducers:Hash<Reducer>):Hash<Reducer> {
    var initialResult:Hash<Reducer> = {};
    return Object
        .keys(reducers)
        .reduce((finalReducer:Hash<Reducer>, key:string):Hash<Reducer> => {
            if (typeof reducers[key] === 'function') {
                finalReducer[key] = reducers[key];
            }
            return finalReducer;
        }, initialResult);
}


// mixed reducer type is not supported, but I want to add them later on.
export function combineReducers<TState>(reducers:Hash<Reducer>):Reducer {
    const finalReducers:Hash<Reducer> = pickReducers<Reducer>(reducers);
    const keys = Object.keys(finalReducers);

    var combinedReducer = <TState extends Hash<any>>(state:TState, action:Action) => {
        if (typeof state === "undefined") state = <any>{};
        var hasChanged:boolean = false;
        var finalState:TState = keys.reduce((_state:TState, key:string):TState => {
            var nextState:TState;
            var previousStateForKey:any = _state[key];
            var nextStateForKey:any = finalReducers[key](
                _state[key],
                action
            );
            hasChanged = hasChanged || previousStateForKey !== nextStateForKey;
            if (!hasChanged) {
                return _state;
            } else {
                nextState = Object.assign({}, _state);
                nextState[key] = nextStateForKey;
                return nextState;
            }
        }, state);

        return hasChanged ? finalState : state;
    };
    return combinedReducer as Reducer;
}

export function passOrCombineReducers<TState>(reducers:Reducer|Hash<Reducer>):Reducer {
    if (typeof reducers !== 'function') {
        return combineReducers<TState>(reducers as Hash<Reducer>);
    } else {
        return reducers as Reducer;
    }
}
