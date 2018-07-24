import createHistory from 'history/createBrowserHistory';
import React, {Component} from 'react'
import {Router} from 'react-router'

/** event for history pushing to store */
export const PUSH_LOCATION = "@@PUSH_LOCATION";
/** event for updating the store (not used, to maintain uni-directional flow.) */
export const UPDATE_LOCATION = "@@UPDATE_LOCATION";

function locationReducer(state, action) {
    if (action.type === PUSH_LOCATION || action.type === UPDATE_LOCATION) {
        return {...state, location: action.location};
    }
    return state;

}

export function connectLocationToStore(store) {
    const history = createHistory();
    const original = store.rootReducer;
    store.rootReducer = (state, action) => locationReducer(original(state, action), action);

    history.listen((location, action) => {
        const {location: oldLocation} = store.getValue();
        if (location !== oldLocation) {
            store.dispatch({
                type: PUSH_LOCATION,
                location
            })
        }
    });

    const initiate = () => store.dispatch({
        type: PUSH_LOCATION,
        location: history.location
    });

    // function* routeProc() {
    //     while (true) {
    //         const {action} = yield take(UPDATE_LOCATION);
    //         history.push(action.location);
    //     }
    // }
    // connectStore(store, routeProc());

    class ConnectedRouter extends Component {
        render() {
            const {children} = this.props;
            return (
                <Router history={history}>{children}</Router>
            )
        }
    }

    return {history, ConnectedRouter, initiate};
}






