export const STORE_KEY = '@@gittor-store';
export const STORAGE_UPDATE_ACTION = "STORAGE_UPDATE_ACTION";

export function connectLocalStorage(store) {
    const original = store.rootReducer;

    function localStorageReducer(state, action) {
        if (action.type === STORAGE_UPDATE_ACTION) {
            const {..._storageState} = action.storage;
            return {...state, ..._storageState};
        }
        return state;
    }

    store.rootReducer = (state, action) => localStorageReducer(original(state, action), action);


    function fromLS() {
        "use strict";
        const store = window.localStorage.getItem(STORE_KEY);
        return JSON.parse(store);
    }

    /** update store when localStorage changes. */
    window.onstorage = () => {
        let storage = fromLS();
        if (typeof storage !== "undefined") {
            store.dispatch({type: STORAGE_UPDATE_ACTION, storage})
        }
    };

    store
        .update$
        // .debounceTime(500)
        .subscribe(({state, action}) => {
            if (action.type === STORAGE_UPDATE_ACTION) return;
            const serialized = JSON.stringify(state);
            try {
                window.localStorage.setItem(STORE_KEY, serialized);
            } catch (e) {
                console.warn(e);
            }
        });
}
