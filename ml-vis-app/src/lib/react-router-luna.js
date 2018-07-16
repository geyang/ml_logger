import {history} from "react-rounter";
const UPDATE_LOCATION = "UPDATE_LOCATION";

export function rounteReducer(state, action) {
    if (action.type === UPDATE_LOCATION && states.location !== action.location) {
        return {...state, location: action.location}
    }
    return state;
}

export function connectStore() {}
