/** Created by ge on 3/27/16. */
export function isArray(obj?: any): boolean {
    return (!!obj && typeof obj === "object" && typeof obj.length !== "undefined");
}
