/** Created by ge on 3/28/16.
 * These effect handling logic are not intended to be pure functions. They are
 * supposed to be aware of the parent thread via the `_this` parameter that is
 * passed in, and are free to call methods of the parent.
 *
 * Spinning up a new process however, is a bit tricky.
 *
 * ### Effect API Todo List
 * done: take,
 * todo: takeEvery,
 * todo: takeLatest,
 * done: select,
 * done: call, SYNC: run generators synchronously, continue after complete.
 * done: apply,
 * done: dispatch (same as `put` in redux-saga. We call `put` `dispatch` instead.),
 * todo: fork, ASYNC: fork out a new process without waiting for it's completion.
 * todo: fork(fn, ...args)
 * todo: fork([context, fn], ...args)
 * todo: takem,
 * todo: all, SYNC: `yield all([gen1, gen2, ...])` starts all generators at the same time, then wait for all to finish.
 * todo: race, SYNC: `yield race([gen1, gen2, ...])` starts all, wait for one to finish and cancel the others.
 * todo: cps,
 * todo: spawn,
 * todo: join,
 * todo: cancel,
 * todo: actionChannel,
 * todo: cancelled,
 * todo: flush,
 * todo: getContext,
 * todo: setContext,
 * todo: throttle,
 * todo: cps(fn, ...args)
 * todo: cps([context, fn], ...args)
 * todo: join(task)
 * todo: cancel(task)
 */


import {Sym, TSym} from "../util/Sym";
import {TEffectBase} from "./interfaces";
import {Action, StateActionBundle} from "luna";
import {TSaga} from "../interfaces";
import {isArray} from "../util/isArray";
import {isIterator} from "../util/isIterator";
import Saga from "../Saga";
import {isPromise} from "../util/isPromise";
import {SynchronousPromise} from "@ge/synchronous-promise";

export interface ITakeEffect extends TEffectBase {
    actionType: any;
}

export const TAKE: TSym = Sym("TAKE");

export function take(actionType: any): ITakeEffect {
    return {type: TAKE, actionType};
}

class TakeError extends Error {
    public original: any;

    constructor(e?: any) {
        super("TakeError in first filter");
        this.original = e;
    }
}

export function takeHandler<T extends StateActionBundle<any>>(effect: ITakeEffect, _this: TSaga<T>): Promise<any> {
    let actionType: any = effect.actionType;
    /* Only take handler uses SynchronousPromise. This is okay because synchronous promise chain breaks the callstack.
    * This will NOT lead to recursive Iterator.next calls. */
    return new SynchronousPromise((resolve, reject) => {
        let isResolved = false;
        _this
            .first((update: StateActionBundle<any>): boolean => {
                let result = false;
                try {
                    if (!update.action.type) {
                        result = false;
                    } else if (update.action.type === actionType) {
                        result = true;
                    } else if (isArray(actionType)) {
                        result = actionType.indexOf(update.action.type) > -1;
                    } else {
                        result = (actionType instanceof RegExp && !!update.action.type.match(actionType));
                    }
                } catch (e) {
                    console.warn(e);
                    reject(new TakeError(e));
                }
                return result;
            })
            .subscribe(
                (update: T) => {
                    isResolved = true;
                    resolve(update);
                }, (err: any) => {
                    isResolved = true;
                    reject(err);
                }, () => {
                    if (!isResolved) reject("take effect stream ended without finding match");
                })
    })
}

export interface IDispatchEffect extends TEffectBase {
    action: Action;
}

export const DISPATCH: TSym = Sym("DISPATCH");

export function dispatch(action: Action): IDispatchEffect {
    return {type: DISPATCH, action};
}

export function dispatchHandler<T extends StateActionBundle<any>>(effect: IDispatchEffect, _this: TSaga<T>): Promise<any> {
    return new SynchronousPromise((resolve, reject) => {
        let isResolved = false;
        /* the actions should be synchronous, however race condition need to be tested. */
        _this
            .take(1) // do NOT use replay here b/c you want to wait for the next event.
            .subscribe(
                (saga: T) => {
                    isResolved = true;
                    if (saga.action.type !== effect.action.type) { // + action id to make sure.
                        reject(`dispatch effect race condition error: ${JSON.stringify(saga.action)}, ${JSON.stringify(effect.action)}`);
                    } else {
                        resolve(saga)
                    }
                },
                (err: any) => {
                    isResolved = true;
                    reject(err);
                },
                () => {
                    // can add flag <Effect>.noCompletionWarning
                    if (!isResolved) reject("dispatch effect stream ended without getting updated state");
                }
            );
        _this.action$.next(effect.action);
    })
}

export interface ICallEffect extends TEffectBase {
    context?: any;
    fn: any;
    args?: Array<any>
}

export const CALL: TSym = Sym("CALL");

/** `call` starts another child process synchronously. The main process will restart after the new child process
 * or promise has already been resolved. */
export function call(fn: any, ...args: any[]): ICallEffect {
    let context: any;
    if (typeof fn === 'function') {
        return {type: CALL, fn, args};
    } else {
        [context, fn] = fn as any[];
        return {type: CALL, fn, args, context};
    }
}

/* Use Saga<TState> instead of TSaga for the instance methods. */
export function callHandler<TState,
    T extends StateActionBundle<TState>>(effect: ICallEffect,
                                         _this: Saga<TState>): Promise<any> {
    let {fn, args, context} = effect;
    try {
        let result: any = fn.apply(context, args);
        // cast iterator `result` to iterable, and use Promise.all to process it.
        if (isIterator(result)) {
            // done: add generator handling logic
            // done: add error handling
            _this.halt();
            return new SynchronousPromise((resolve, reject) => _this.forkChildProcess(
                new Saga(result),
                reject, // how to handle error?
                () => {
                    _this.resume();
                    resolve();
                }));
        } else if (isPromise(result)) {
            return result;
        } else {
            return SynchronousPromise.resolve(result);
        }
    } catch (e) {
        return SynchronousPromise.reject(e);
    }
}

export interface IForkEffect extends TEffectBase {
    context?: any;
    fn: any;
    args?: Array<any>
}

export const FORK: TSym = Sym("FORK");

/** `fork` starts a child process asynchronously. The main process will not block.
 * */
export function fork(fn: any, ...args: any[]): IForkEffect {
    let context: any;
    if (typeof fn === 'function') {
        return {type: FORK, fn, args};
    } else {
        [context, fn] = fn as any[];
        return {type: FORK, fn, args, context};
    }
}

export function forkHandler<TState,
    T extends StateActionBundle<TState>>(effect: IForkEffect,
                                         _this: Saga<TState>): Promise<any> {
    let {fn, args, context} = effect;
    try {
        let result: Iterator<TState> | Promise<any> = fn.apply(context, args);
        // cast iterator `result` to iterable, and use Promise.all to process it.
        if (isIterator(result)) {
            const childProcess: Saga<TState> = new Saga(result as Iterator<TState>);
            _this.forkChildProcess(childProcess);
            // todo: return a process id to allow process cancellation
            return SynchronousPromise.resolve(childProcess);
        } else if (isPromise(result)) {
            return result as Promise<any>;
        } else {
            return SynchronousPromise.resolve(result);
        }
    } catch (e) {
        return SynchronousPromise.reject(e);
    }
}

export interface ISpawnEffect extends TEffectBase {
    context?: any;
    fn: any;
    args?: Array<any>
}

export const SPAWN: TSym = Sym("SPAWN");

/** `spawn` starts a child process asynchronously. without bubbling up the errors. This way the parent won't terminate
 * on child unintercepted errors. */
export function spawn(fn: any, ...args: any[]): ISpawnEffect {
    let context: any;
    if (typeof fn === 'function') {
        return {type: SPAWN, fn, args};
    } else {
        [context, fn] = fn as any[];
        return {type: SPAWN, fn, args, context};
    }
}

export function spawnHandler<TState,
    T extends StateActionBundle<TState>>(effect: ISpawnEffect,
                                         _this: Saga<TState>): Promise<any> {
    let {fn, args, context} = effect;
    try {
        let result: Iterator<TState> | Promise<any> = fn.apply(context, args);
        // cast iterator `result` to iterable, and use Promise.all to process it.
        if (isIterator(result)) {
            const childProcess: Saga<TState> = new Saga(result as Iterator<TState>);
            _this.forkChildProcess(childProcess, null, null, true);
            // todo: return a process id to allow process cancellation
            return SynchronousPromise.resolve(childProcess);
        } else if (isPromise(result)) {
            return result as Promise<any>;
        } else {
            return SynchronousPromise.resolve(result);
        }
    } catch (e) {
        return SynchronousPromise.reject(e);
    }
}

/* apply is call's alias with context */
export function apply(context: any, fn: any, ...args: any[]): ICallEffect {
    return {type: CALL, fn, args, context};
}


export interface ISelectEffect extends TEffectBase {
    selector?: string;
}

export const SELECT: TSym = Sym("SELECT");

export function select(selector?: string): ISelectEffect {
    return {type: SELECT, selector};
}

export function selectHandler<T extends StateActionBundle<any>>(effect: ISelectEffect, _this: TSaga<T>): Promise<any> {
    let selector = effect.selector;
    return new SynchronousPromise((resolve, reject) => {
        let isResolved = false;
        // [DONE] to populate the replay$ subject, use sagaConnect's SAGA_CONNECT_ACTION update bundle.
        _this.replay$.take(1)
            .map((update: StateActionBundle<any>): any => {
                if (typeof selector === "undefined") {
                    return update.state;
                } else if (typeof selector === "string") {
                    return update.state[selector]
                }
            })
            .subscribe(
                (value: any) => {
                    isResolved = true;
                    resolve(value)
                },
                (err: any) => {
                    isResolved = true;
                    reject(err);
                },
                () => {
                    if (!isResolved) reject("dispatch effect stream ended without getting updated state");
                }
            );
    });
}
