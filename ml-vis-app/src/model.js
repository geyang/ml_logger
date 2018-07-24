import {Store} from "luna"
import {sagaConnect} from 'luna-saga';
import {registerStore} from "./lib/react-luna";
import {
    directoryProc,
    locationProc,
    metricsDownloadProc,
    metricsProc,
    removeProc,
    rootReducer,
    searchProc
} from "./lib/file-api";
import {connectLocationToStore} from "./lib/routeStoreConnect";

import createHistory from "history/createBrowserHistory";
import {connectLocalStorage} from "./lib/connect-local-storage";

const history = createHistory();
const location = history.location;

function storageSelector({searchQuery, chartKeys, showComparison, yMin, yMax}) {
    return {searchQuery, chartKeys, showComparison, yMin, yMax};
}


export const store$ = new Store(rootReducer);
// store$.update$.subscribe(({state, action}) => console.log(state, action));
registerStore(store$);
const {syncStore} = connectLocalStorage(store$, storageSelector);
syncStore();
export const {ConnectedRouter, initiate: initiateLocationStore} = connectLocationToStore(store$);
initiateLocationStore();
sagaConnect(store$, metricsProc());
sagaConnect(store$, locationProc());
sagaConnect(store$, directoryProc());
sagaConnect(store$, searchProc());
/* the ordering here somehow matters. */
sagaConnect(store$, metricsDownloadProc());
sagaConnect(store$, removeProc());


// // 1. get saga to run [5 min; ended up 2 hours.]
// // 2. connect to file-events [5 min]
// // 3. add experiment collection [5 min]
// // 4. add selected experiments [5 min]
// // 5. add experiment pickle objects [5 min]
// // 5. add experiment dashboard [5 min]
// // 6. add learning curve component [5 min]
// // 7. add comparison plot between multiple experiments [5 min]
