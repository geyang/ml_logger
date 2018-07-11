/** Created by ge on 3/27/16. */
import Saga from "./Saga";
import {Action} from "luna";
import {CALLBACK, ICallbackFunc} from "./util/isCallback";
import {isAction} from "./util/isAction";
import {isFunction} from "./util/isFunction";

interface TestAction extends Action {
    payload?: any;
}

jasmine.DEFAULT_TIMEOUT_INTERVAL = 100;
describe("saga.simple.spec: Promise Handling", function () {
    it("process runner should work", function (done: () => void) {
        let thunk_has_ran = false;
        let result;

        function thunk(): Action {
            thunk_has_ran = true;
            return {type: "DEC"};
        }

        function dummyAsyncFunc(cb: ICallbackFunc) {
            cb(null, "** async RESULT **");
        }

        function dummyAsyncFuncThrowingError(cb: ICallbackFunc) {
            cb("** async ERROR **");
        }

        function* idMaker(): Iterator<any> {
            // you can yield number
            yield 0;

            // you can yield undefined
            yield;

            // you can yield action
            yield {type: "INC"};
            // and you can bypass the action detection
            yield {type: "INC", __isNotAction: true};

            // you can yield thunk, but thunks are not executed unless
            // there is a store with `store.dispatch` method.
            // In this case, because no store$ is attached, this thunk
            // is not executed. And we need to make sure that is the case.
            result = yield thunk;
            expect(result).toBe(thunk);
            expect(thunk_has_ran).toBe(false);

            // **advanced**
            // you can use the yield-yield syntax with the CALLBACK token
            // Here the middleware intercepts the callback token, returns
            // a callback function into the generator, which allows
            // the async function to execute (the `dummyAsyncFunc`)
            result = yield dummyAsyncFunc(yield CALLBACK);
            expect(result).toBe("** async RESULT **");

            // we can catch error synchronously in the callback
            try {
                result = yield dummyAsyncFuncThrowingError(yield CALLBACK);
            } catch (err) {
                console.warn(err);
                expect(err).toBe("** async ERROR **");
            }

            result = yield Promise.resolve(1);
            expect(result).toBe(1);
            let i: number = 0, j: number;
            while (i <= 3) {
                j = yield i as number;
                expect(i).toBe(j);
                i++
            }

            /* now we can call it end. Remember, we can't just
             yield the done function and expect it to be executed because
             no store object is attached in this specification.
             As a result, here call done explicitly.*/

            /* note: returned value is logged and evaluated. */
            return done();
        }

        let saga = new Saga<TestAction>(idMaker());
        let startDate = Date.now();
        saga.log$.subscribe(
            (_: any): any => console.log("log: ", _),
            null,
            (): any => {
                console.log(`saga execution took ${(Date.now() - startDate) / 1000} seconds`);
            }
        );
        saga.action$.subscribe((action: any): any => {
            if (!isAction(action)) throw console.error('action is ill formed.', action);
            else console.log("action: ", action)
        });
        saga.thunk$.subscribe((thunk: any): any => {
            if (!isFunction(thunk)) throw console.error('thunk is ill formed.', thunk);
            else console.log("Thunk: ", thunk)
        });
        saga.subscribe({error:(err: any): any => {
            console.warn("saga.error$", err);
        }});
        saga.run();
    });
});


