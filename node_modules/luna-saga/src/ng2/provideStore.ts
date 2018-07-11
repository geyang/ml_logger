/** Created by ge on 12/17/15. */
import {Reducer, Hash} from "./../interfaces";
import {Store} from "./../Saga";
import {createStore} from "./../createStore";

// for angular2
import "reflect-metadata";
import {provide} from "angular2/core";

export function provideStore<TState>(reducer:Reducer|Hash<Reducer>, initialState:TState):any[] {
    return [
        provide(Store, {useFactory: createStore(reducer, initialState)})
    ]
}
