/** Created by ge on 4/1/16. */
export function isNull(obj?: any): boolean {
    return (obj === null && typeof obj === "object");
}
