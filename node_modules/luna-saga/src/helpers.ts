/**
 * Created by ge on 12/7/16.
 *
 * Usage Example:
 * yield call(delay, 500)
 *
 * */
import {call, spawn, take} from "./effects/effectsHelpers";

export function delay(ms: number): Promise<any> {
    return new Promise((resolve) => setTimeout(() => resolve(true), ms))
}

/* Helper Processes */
/** throttle process: Takes in a task function, a trigger object <RegExp, string, TSym>, input interval, and flag for triggering on falling edge. */
export function* throttle(task: Function, trigger: void | any, interval = 300, falling = true): Generator {

    let rising, trail, proc;

    function* takeOne() {
        // take only one.
        yield take(trigger);
        trail = true;
    }

    while (true) {
        yield take(trigger);
        rising = true;
        while (trail && falling || rising) {
            if (rising) rising = false;
            trail = false;
            // take one from the rest
            proc = yield spawn(takeOne);
            yield spawn(task);
            yield call(delay, interval);
            if (!proc.isStopped) proc.complete(); // make sure we remove the child process from parent.
        }
    }
}
