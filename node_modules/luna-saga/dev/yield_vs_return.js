/** Created by ge on 12/26/17. */

function* proc() {
    yield 0;
    return "returned value"
}
const p = proc();
let r = p.next();
console.log(r);
r = p.next();
console.log(r);
