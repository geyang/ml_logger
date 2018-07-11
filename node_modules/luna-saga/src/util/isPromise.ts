/** Created by ge on 3/27/16. */
export function isPromise(obj?: any): boolean {
    return (!!obj && !!obj.then);
}
