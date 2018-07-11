/** Created by ge on 12/25/17. */
import {Subject, Observable} from "rxjs";

const subject = new Subject();

subject.subscribe({
    next: (v) => console.log('observerA: ' + v)
});
subject.subscribe({
    next: (v) => console.log('observerB: ' + v)
});

const observable = Observable.from([1, 2, 3]);

observable.subscribe(subject);
observable.subscribe((value)=>console.log("value", value));
