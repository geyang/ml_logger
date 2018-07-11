//@flow
import Saga, {SAGA_CONNECT_ACTION, take} from "../dist";

export async function async_fn() {
    return await new Promise((res, rej) => setTimeout(()=>res(10), 1000));
}

function* Proc() {
    console.log('**************');
    const {state, update} = yield take('TEST_ACTION');
    console.log(state);
    const r = yield async_fn();
    console.log('=============');
    console.log(r);
}

const proc = new Saga(Proc());
proc.run();
proc.next({state: "a string", action: {type: SAGA_CONNECT_ACTION}});
proc.next({state: "still a string", action: {type: "TEST_ACTION"}});
