/** Created by ge on 12/4/15. */
import {Action, Thunk, Reducer, Hash, StateActionBundle} from "luna";
import {isCallbackToken} from "./util/isCallback";
import {isPromise} from "./util/isPromise";
import {isAction} from "./util/isAction";
import {isEffect} from "./effects/isEffect";
import {isFunction} from "./util/isFunction";
import {Subject, ReplaySubject, Observable, Observer} from "rxjs";
import {ISubscription} from 'rxjs/Subscription';
import {isUndefined} from "./util/isUndefined";
import "setimmediate"; // refer to https://github.com/YuzuJS/setImmediate/issues/48
import {TEffectBase} from "./effects/interfaces";
import {TSym, Sym} from "./util/Sym";
import {
    TAKE, FORK, SPAWN, DISPATCH, CALL, SELECT,
    ITakeEffect, IForkEffect, ISpawnEffect, IDispatchEffect, ICallEffect, ISelectEffect,
    takeHandler, forkHandler, spawnHandler, dispatchHandler, callHandler, selectHandler
} from "./effects/effectsHelpers";
import {CALLBACK_START, CallbackReturn, CallbackThrow} from "./util/isCallback";
import {isNull} from "./util/isNull";

export const SAGA_CONNECT_ACTION: TSym = Sym('SAGA_CONNECT_ACTION');

export class AutoBindSubject<T> extends Subject<T> {
    constructor() {
        super();
        /* bind next method */
        this.next = this.next.bind(this);
    }
}

/** ProcessSubject
 * Subject emits a termination signal via `this.term$` when completed, then completes
 * the stream and then removes all subscribers.
 */
export class ProcessSubject<T> extends AutoBindSubject<T> {
    public term$: Observable<any>;
    private _term$: Subject<any>;
    public subscriptions: Array<ISubscription>;

    constructor() {
        super();
        this.subscriptions = [];
        this._term$ = new Subject<any>();
        /* term$ is used to signal other observers of the end of ProcessSubject */
        this.term$ = this._term$.concat(Observable.of(true));
        this.destroy = this.destroy.bind(this);
        /* call this.distroy on complete and error */
        this.subscribe(null, this.destroy, this.destroy)
    }

    subscribeTo($: Observable<T>): void {
        this.subscriptions.push($.takeUntil(this.term$).subscribe(this.next));
    }

    /* finally is an operator not a handle. Destroy doesn't exist on Sujects, so it is safe to use it here. */
    destroy(): void {
        this.subscriptions.forEach((s) => s.unsubscribe());
        this.subscriptions.length = 0;
        this._term$ = null;
        this.term$ = null;
    }
}

export const CHILD_ERROR = Sym("CHILD_ERROR");

class ChildErr {
    type: TSym = CHILD_ERROR;
    public err: any | undefined;

    constructor(err?: any) {
        this.err = err;
    };
}

class NO_PROCESS_ITERATOR extends Error {
    constructor() {
        super("Saga requires a process iterator as the constructor input.")
    }
}

export default class Saga<TState> extends ProcessSubject<StateActionBundle<TState>> {
    private value: StateActionBundle<any>;
    private process: Iterator<any>;
    public isHalted: boolean = false;
    private childProcesses: Array<Saga<TState>> = [];
    public replay$: ReplaySubject<StateActionBundle<TState>>;
    public log$: Subject<any>;
    public action$: Subject<any>;
    public thunk$: Subject<() => any>;
    private nextResult: (res?: any) => void;
    private nextThrow: (err?: any) => void;
    private nextYield: (res?: any, err?: any) => void;
    private evaluateYield: (res?: any, err?: any) => void;

    constructor(proc: Iterator<any>) {
        super();// replay just no past event, just broadcast new ones.
        this.nextYield = this._nextYield.bind(this);
        this.evaluateYield = this._evaluateYield.bind(this);
        this.nextResult = this._next.bind(this);
        this.nextThrow = this._throw.bind(this);

        /* this is just the process generator */
        this.process = proc;
        /* Various signal streams. OUTPUT ONLY. Use internal error/complete handle for signaling. */
        this.log$ = new AutoBindSubject<any>();
        this.action$ = new AutoBindSubject<Action>();
        this.thunk$ = new AutoBindSubject<() => any>();


        /* use a replay subject to maintain state for `select` operator.*/
        this.replay$ = new ReplaySubject<StateActionBundle<TState>>(1);
        this.subscribe(this.replay$);
    }

    next(value: StateActionBundle<TState>) {
        // proper behavior: play main thread,
        this.value = value;
        // route the bundles into child processes.
        if (!this.isHalted) super.next(value); // notifies the super Subject Object.
        if (this.childProcesses) {
            this.childProcesses.forEach(proc => proc.next(value));
        }
    }

    run() {
        if (typeof this.process === "undefined") throw new NO_PROCESS_ITERATOR();
        this.nextYield();
        return this;
    }

    halt() {
        this.isHalted = true;
    }

    resume() {
        this.isHalted = false;
    }

    removeChildProcess(childProc: Saga<TState>) {
        if (this.isStopped) return;
        const ind = this.childProcesses.indexOf(childProc);
        if (ind == -1) console.warn('child process does not exist');
        else this.childProcesses.splice(ind);
    }

    destroy(): void {
        /* called by binding in ProcessSubject. destroy all references to release from memory */
        this.process = null;
        this.replay$ = null;
        this.log$ = null;
        this.thunk$ = null;
        this.action$ = null;
        this.childProcesses = null;
        super.destroy();
    }

    error(err: any): void {
        this.log$.complete();
        /* when termination is triggered by error$ stream, error$.complete double call raise exception. */
        this.thunk$.complete();
        this.action$.complete();
        /* Complete the parent first, to make sure that `this.term$` signals termination. */
        super.error(err);
    }

    complete(): void {
        this.log$.complete();
        /* when termination is triggered by error$ stream, error$.complete double call raise exception. */
        this.thunk$.complete();
        this.action$.complete();
        /* Complete the parent first, to make sure that `this.term$` signals termination. */
        super.complete();
    }

    _next(res?: any): void | any {
        //todo: refactor _nextYield
        return this.nextYield(res);
    }

    _throw(err?: any): void | any {
        //todo: refactor _nextYield
        return this.nextYield(null, err);
    }

    /* Topologically a glorified wrapper for this.process.next and this.process.throw. */
    _nextYield(res?: any, err?: any): void | any {
        let yielded: IteratorResult<any>;
        if (this.isStopped) return console.warn('Saga: yield call back occurs after process termination.');
        /* Handle Errors */
        if (typeof err !== "undefined" && !isNull(err)) {
            /* [DONE] we need to raise from Saga to the generator.*/
            try {
                /* Do NOT terminate, since this error handling happens INSIDE SAGA, eg. for callback functions */
                yielded = this.process.throw(err);
            } catch (e) {
                /* print error, which automatically completes the process.*/
                this.error(e);
                /* break the callback stack. */
                throw new Error('THIS SHOULD NEVER BE HIT');
            }
        } else {
            /* if an error occur not through `yield`, we will need to intercept it here.*/
            try {
                yielded = this.process.next(res);
            } catch (e) {
                /* The process has raised an exception */
                let process = this.process; // maintain a copy of the process b/c this.error removes it.
                this.error(e); // we need to terminate this saga before throwing the error back to the process.
                /* we throw this error back, which terminates the generator. */
                process.throw(e);
                process = null;
                /* the Generator is already running error usually means multiple recursive next() calls happened */
                throw new Error('THIS SHOULD NEVER SHOW B/C OF THROW')
            }
        }
        /* Now evaluate the yielded result... */
        this.evaluateYield(yielded);
    }

    _evaluateYield(yielded: IteratorResult<any>): void {
        if (!yielded) {
            /* should never hit here. Also <saga> should be completed at this point
             * already, so we can't log to error$ because it is already `null`.
             * We log to console instead.
             * If this is hit, something is wrong.
             */
            console.error('`yielded` is undefined. This is likely a problem with `luna-saga`.');
            throw "`yielded` need to exist";
        }
        if (!!yielded.done) {
            // todo: take care of return calls, change logic flow.
            /* Done results *always* have value undefined. */
            this.complete();
            return;
        }
        this.log$.next(yielded.value);
        if (isUndefined(yielded.value)) {
            // What the generator gets when it `const variable = yield;`.
            // we can pass back a callback function if we want.
            setImmediate(() => this.nextResult(yielded.value));
        } else if (isFunction(yielded.value)) {
            this.thunk$.next(yielded.value);
            setImmediate(() => this.nextResult(yielded.value));
        } else if (isCallbackToken(yielded.value)) {
            // no need to save the yielded result.
            this.log$.next(CALLBACK_START);
            this.process.next((err?: any, res?: any): any | void => {
                // does not support (, ...opts: Array<any>)
                /* synchronous next call */
                if (!!err) {
                    this.log$.next(CallbackThrow(err));
                    // need to break the callstack b/c still inside process.next call and this callback is synchronous.
                    setImmediate(() => this.nextThrow(err));
                } else {
                    this.log$.next(CallbackReturn(res));
                    // need to break the callstack b/c still inside process.next call and this callback is synchronous.
                    setImmediate(() => this.nextResult(res));
                }
            });
        } else if (isPromise(yielded.value)) {
            let p = yielded.value;
            p.then(this.nextResult, this.nextThrow)
        } else if (isEffect(yielded.value)) {
            /* Promise.then call is in fact asynchronous. This causes consecutive `take`s to miss store actions fired
            synchronously. */
            this._executeEffect(yielded.value).then(this.nextResult, this.nextThrow);
        } else {
            if (isAction(yielded.value)) this.action$.next(yielded.value);
            /** speed comparison for 1000 yields:
             * no callback: 0.110 s, but stack overflow at 3900 calls on Chrome.
             * setTimeout: 4.88 s.
             * setZeroTimeout: 0.196 s, does not stack overflow.
             * setImmediate cross-platform package: 0.120 s. fantastic.
             */
            setImmediate(() => this.nextResult(yielded.value));
        }
    }

    _executeEffect(effect: TEffectBase & any): Promise<any> {
        let type: TSym = effect.type;
        if (type === TAKE) {
            let _effect: ITakeEffect = effect;
            return takeHandler(_effect, this);
        } else if (type === FORK) {
            let _effect: IForkEffect = effect;
            return forkHandler(_effect, this);
        } else if (type === SPAWN) {
            let _effect: ISpawnEffect = effect;
            return spawnHandler(_effect, this);
        } else if (type === DISPATCH) {
            let _effect: IDispatchEffect = effect;
            return dispatchHandler(_effect, this);
        } else if (type === CALL) {
            let _effect: ICallEffect = effect;
            return callHandler(_effect, this);
        } else if (type === SELECT) {
            let _effect: ISelectEffect = effect;
            return selectHandler(_effect, this);
        } else {
            return Promise.reject(`executeEffect Error: effect is not found ${JSON.stringify(effect)}`);
        }
    }

    getValue() {
        return this.value;
    }


    /** Starts a single child process, stop the current process, and resume afterward. */
    forkChildProcess(newProcess: Saga<TState>,
                     onError?: (err: any) => void,
                     onFinally?: () => void,
                     noBubbling?: Boolean) {
        this.childProcesses.push(newProcess);
        newProcess.action$.takeUntil(this.term$).subscribe(this.action$.next);
        newProcess.thunk$.takeUntil(this.term$).subscribe(this.thunk$.next);
        newProcess.log$.takeUntil(this.term$).subscribe(this.log$.next);
        if (!noBubbling) newProcess.subscribe({error: (err) => this.error(new ChildErr(err))});
        /* We complete the process when the newProcess.error(e) is called. */
        if (onError) newProcess.takeUntil(this.term$).subscribe({error: onError});
        const fin = () => {
            this.removeChildProcess(newProcess);
            /* release newProcess from memory here. */
            newProcess = null;
            if (typeof onFinally == 'function') onFinally()
        };
        newProcess.subscribe({error: fin, complete: fin});

        // trigger the first subscription event so that child process has the current state(and action).
        newProcess.run();
        let currentValue = this.getValue();
        newProcess.next({
            state: currentValue ? currentValue.state : undefined,
            action: {type: SAGA_CONNECT_ACTION}
        } as StateActionBundle<TState>);
    }
}


