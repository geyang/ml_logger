/** Created by ge on 12/6/16.
 * Usage Example
 * selector(key/selectionFunction/arrayOf'keys/etc, component)
 * */
import React from "react";

const DEFAULT_KEY = "@@luna-store";
const stores = {};

export function registerStore(store, key = DEFAULT_KEY) {
    stores[key] = store;
}

export default function selector(
    selectorFunction,
    Component,
    dispatch = false,
    storeKey = DEFAULT_KEY
) {
    return class SelectContainer extends React.Component {

        constructor(props) {
            super(props);
            this.store$ = stores[storeKey];
            if (!this.store$) console.warn('no store has been registered. Please call registerStore first!');
            this.storeToState = this._storeToState.bind(this);
        }

        _storeToState(store) {
            if (store !== this.state) this.setState(selectorFunction(store));
        }

        componentWillMount() {
            this.subscription = this.store$.subscribe(this.storeToState);
        }

        componentWillUnmount() {
            this.subscription.unsubscribe()
        }

        render() {
            if (!this.state) return <div>state is not defined</div>;
            let props = {...this.state, ...this.props};
            if (dispatch) props.dispatch = this.store$.dispatch;
            return <Component {...props}/>
        }
    }
}

export function identity(_) {
    return _;
}
