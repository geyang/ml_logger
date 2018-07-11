/** Created by ge on 12/25/16. */
export function isGenerator(fn?: any): boolean {
    if (typeof fn !== "function") return false;
    // console.log(fn.prototype.constructor);
    return fn.prototype.constructor.name === "GeneratorFunctionConstructor";
}
