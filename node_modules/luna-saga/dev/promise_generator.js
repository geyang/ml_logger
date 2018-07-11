/** Created by ge on 12/25/17. */
"use strict";

function count(): number {
    return 42;
}
async function countAsync(): Promise<number> {
    return count();
}
const c = countAsync();
console.log(c);

