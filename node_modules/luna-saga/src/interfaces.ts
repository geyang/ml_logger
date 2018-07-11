/** Created by ge on 12/6/15. */
import {Action, Thunk} from "luna";
import {Subject} from "rxjs";
import {ProcessSubject} from "./Saga";

export interface TSaga<T> extends ProcessSubject<T> {
    replay$: Subject<T>;
    log$: Subject<any>;
    action$: Subject<Action>;
    thunk$: Subject<Thunk>;
    run: () => void;
    // below exist on super.
    // next: (obj: any) => void;
    // error: (err: any) => void;
    // complete: () => void;
    // destroy: () => void;
}
