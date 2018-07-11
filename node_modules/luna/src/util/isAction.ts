/** Created by ge on 12/27/16. */
export function isAction(obj?: any): boolean {
    return (!!obj && !!(obj.type));
}
