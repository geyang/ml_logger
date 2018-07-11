/** Created by ge on 3/27/16. */
import {TAKE, FORK, SPAWN, DISPATCH, CALL, SELECT} from "./effectsHelpers";
let effects = [TAKE, FORK, SPAWN, DISPATCH, CALL, SELECT];
export function isEffect(obj?: any): boolean {
    return (!!obj && obj.type && effects.indexOf(obj.type) > -1);
}
