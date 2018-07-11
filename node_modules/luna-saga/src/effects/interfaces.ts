import {TSym} from "../util/Sym";
/** Created by ge on 3/28/16. */
export interface TEffectBase {
    type: TSym;
    [key:string]:any;
}
