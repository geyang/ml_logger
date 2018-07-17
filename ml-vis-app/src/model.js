import {Store} from "luna"
import {sagaConnect} from 'luna-saga';
import {registerStore} from "./lib/react-luna";
import {directoryProc, locationProc, metricsProc, removeProc, rootReducer} from "./lib/file-api";
import {connectLocationToStore} from "./lib/routeStoreConnect";

import createHistory from "history/createBrowserHistory";
import {connectLocalStorage} from "./lib/connect-local-storage";

const history = createHistory();
const location = history.location;

export const store$ = new Store(rootReducer);
registerStore(store$);
export const {ConnectedRouter, initiate: initiateLocationStore} = connectLocationToStore(store$);
store$.update$.subscribe((state, action) => console.log(state, action));
sagaConnect(store$, metricsProc());
sagaConnect(store$, directoryProc());
sagaConnect(store$, locationProc());
sagaConnect(store$, removeProc());

// connectLocalStorage(store$);
initiateLocationStore();

// store$.dispatch({type: "GO_TO"});

// const experiment = {
//     currentDirectory: "",
//     metricFiles: [],
//     textFiles: [],
//     logFiles: [],
//     files: [],
//     imageFiles: [],
//     movieFiles: []
// };
//
//
// let reducer = function (state = {}, action) {
//     if (action.type === INIT_STORE) {
//         console.log('hey');
//         return state
//     } else if (action.type === 'INC') {
//         console.log('INC');
//         return state
//     }
//     return state
// };
//
// // 1. get saga to run [5 min; ended up 2 hours.]
// // 2. connect to file-events [5 min]
// // 3. add experiment collection [5 min]
// // 4. add selected experiments [5 min]
// // 5. add experiment pickle objects [5 min]
// // 5. add experiment dashboard [5 min]
// // 6. add learning curve component [5 min]
// // 7. add comparison plot between multiple experiments [5 min]
//
// //list of endpoints and handles
// const protocol = 'http';
// const host = "54.71.92.65:8082";
// const eventSrc = `${protocol}://${host}/file-events`;
// const fileRoot = `${protocol}://${host}/files`;
//
// export const store$ = new Store(reducer);
// store$.dispatch({type: "INC"});
// store$.subscribe((state) => console.log(state));
//
// // store$.subscribe
// function* proc() {
//     const eventOutputContainer = document.getElementById("event");
//     const evtSrc = new EventSource(eventSrc);
//     evtSrc.onmessage = function (e) {
//         // console.log(e.data);
//     };
//     while (true) try {
//         console.log('========================');
//         yield call(delay, 1000);
//     } catch (e) {
//         console.error(e);
//     }
//
// }
//
// const p = proc();
// sagaConnect(store$, proc());
