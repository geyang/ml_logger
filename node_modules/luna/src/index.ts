/** Created by ge on 12/4/15. */
export * from "./interfaces";
export {combineReducers, passOrCombineReducers} from "./util/combineReducers";
export {Store, INIT_STORE, INIT_STORE_ACTION} from "./Store";
export {createStore} from "./createStore";
/*remove dependency on angular2*/
//export {provideStore} from "./ng2/provideStore";
//export {StoreService} from "./ng2/StoreService";
