/** Created by ge on 12/19/15.
 *
 * # NOTE:
 *
 * This is the parent class for store services in an angular2 project.
 *
 * I found it easier to organize the reducer and types as angular2 classes, and use
 * the dependency injection to automatically setup the rootStoreService.
 */
import {Reducer} from "./../interfaces";

export class StoreService<TState> {
    initialState:TState;
    reducer:Reducer;
    types:any;
    $:any;
    actions:any;

    constructor() {
        this.$ = {};
        this.types = {};
        this.actions = {};

        // # Typical coding patterns in the constructor:
        //
        // 1. Compose the reducer of your dependencies and save it to this.reducer
        // 2. Collect all streams from lower level dependencies to this.$
        // 3. Now initialize your store if this is the root store, or assemble the child states
        //    and assign it to `this.initialState`.
        // 4. It is also convenient to collect actionCreators. They will be dispatched with
        //    `this` keyword bound to the rootStore object.
    }

    onStoreInit (store:TState):void {
    }
}
