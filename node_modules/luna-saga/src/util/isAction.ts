/** Created by ge on 3/27/16. */
/// <reference path="./lodash.isplainobject.d.ts"/>
import isPlainObject = require("lodash.isplainobject");
export function isAction(obj?: any): boolean {
    return (!!obj && typeof obj.type !== "undefined" && isPlainObject(obj) && !obj.__isNotAction)
}
