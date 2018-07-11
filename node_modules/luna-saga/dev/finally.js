/** Created by ge on 12/25/17. */
import Saga from "../dist";

let r;
function* proc(){
    yield "hey";
    console.log('--------')
}
// what do I want to do
// I want to test if saga final works
const s = new Saga(proc());
s.run();
s.next();
// s.complete();
s.error();

// import {Subject} from "rxjs";
//
// const subject = new Subject();
//
// subject
//     .finally(() => console.log('First finally called'))
//     .subscribe(
//         () => {
//         }, () => {
//         });  // This error handler will result in the second finally being called.
//
// subject
//     .finally(() => console.log('Second finally called'))
//     .subscribe(() => {
//     });
//
// subject.error('error');
