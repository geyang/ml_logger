/** Created by ge on 12/25/16. */
export function isIterator(obj?: any): boolean {
    return (!!obj && typeof obj.next === 'function');
}
