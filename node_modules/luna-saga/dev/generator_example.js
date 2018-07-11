/** Created by ge on 12/25/17.
 * Note: in this new node/browser environment, a generator called after throwing an error does NOT raise the
 * 'generator is already running' error.
 *
 * */
import "should"

const CATCH = true;

function* gen(consumer_catching = 0) {
    let r;
    r = yield "hey";
    try {
        throw new Error("** exception **");
    } catch (e) {
        should(e.message).be.equal("** exception **")
    }
    if (!!consumer_catching) {
        throw new Error("** exception caught by consumer **");
    } else {
        throw new Error("** uncaught exception **");
    }
    console.error('gen#L:14 THIS WILL NEVER SHOW');
}

function consumer(catching = 0) {
    let y;
    const i = gen(catching);
    const hey = i.next("first call");
    should(hey.value).be.equal("hey");
    try {
        y = i.next("won't arrive");
    } catch (e) {
        if (catching === 0) {
            should(e.message).be.equal("** uncaught exception **");
            try {
                i.next()
            } catch (e) {
                console.log(e);
                should(e.message)
            }
        } else if (catching === 1) {
            should(e.message).be.equal("** exception caught by consumer **");
            console.log('THIS WILL PRINT, but the line after will NOT.');
            i.throw(Error('New Error given by consumer'));
            console.log('THIS WILL NEVER PRINT, b/c it is after iterator.throw.')
        } else if (catching === 2) {
            should(e.message).be.equal("** exception caught by consumer **");
            let exception;
            try {
                i.next("should raise error");
            } catch (e) {
                exception = e;
            }
            /* some how this is not behavig */
            should(exception).be.defined()
        }
    }
    y = i.next("doesn't matter");
    should(y.done).be.equal(true);
    should(y.value).be.undefined();
    y = i.next("doesn't matter");
    should(y.done).be.equal(true);
    should(y.value).be.undefined();
    console.log("this will NOT print");
}

// comment this out to run the next task
consumer(1);

function example() {
    function* throwing() {
        console.log('Generator entered, yielding first value');
        yield 1;
        console.log('Generator asked for second value - will go bum');
        throw new Error("You can only call this generator once, sorry!");
        console.log('Will never get here');
        yield 3;
    }

    const throwingGenerator = throwing();

    throwingGenerator.next();
    try {
        throwingGenerator.next();
    } catch (e) {
        console.error(e);
        throwingGenerator.next();
    }
    /* Now try to do this in the console: */
}

example();
