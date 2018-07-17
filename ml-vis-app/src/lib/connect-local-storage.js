export const STORE_KEY = '@@gittor-store';
export const STORAGE_UPDATE_ACTION = "STORAGE_UPDATE_ACTION";

export function connectLocalStorage(store, storeSelector = (_) => _, syncOnStorageUpdate = false) {
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
        const store = window.localStorage.getItem(STORE_KEY);
        return JSON.parse(store);
    }

    /** update store when localStorage changes. */
    const syncStore = () => {
        let storage = fromLS();
        if (typeof storage !== "undefined") {
            store.dispatch({type: STORAGE_UPDATE_ACTION, storage})
        }
    };
    if (syncOnStorageUpdate) window.onstorage = syncStore;

    store
        .update$
        // .debounceTime(500)
        .subscribe(({state, action}) => {
            if (action.type === STORAGE_UPDATE_ACTION) return;
            // this selector allows you to save only selected fields of the state to local storage.
            // they are then passed to the store on storage update and initialization.
            const serialized = JSON.stringify(storeSelector(state));
            try {
                window.localStorage.setItem(STORE_KEY, serialized);
            } catch (e) {
                console.warn(e);
            }
        });

    return {syncStore};
}
