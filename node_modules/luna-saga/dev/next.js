/** Created by ge on 12/22/17. */
class S {
    next() {
        console.warn('class S next() method');
    }
}

class A extends S {
    constructor() {
        super();
        // I was using `super` instead of this. Big mistake.
        this.next = this.next.bind(this)
    }
    next(){
        console.log('class A next() method')
    }
}

const a = new A();
a.next();
