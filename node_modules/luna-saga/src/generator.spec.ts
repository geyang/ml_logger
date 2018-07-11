/** Created by ge on 3/27/16. */

describe("generator.spec: Generator Example", function () {
    it("should work with loader and webpack", function () {

        function* idMaker(): Iterator<any> {
            let index = 0;
            while (index < 3)
                yield index++;
            return "this is finished";
        }

        const gen = idMaker();

        expect(gen.next().value).toBe(0);
        expect(gen.next().value).toBe(1);
        expect(gen.next().value).toBe(2);
        const last = gen.next();
        expect(last.value).toBe("this is finished");
        expect(last.done).toBe(true);
    });

    it("has a simple async pattern", function (done: any) {

        let asyncFn = (cb: (obj: any) => any) => {
            setTimeout(() => {
                cb("[async result]");
                return "==> asyncFn return <==";
            }, 100);
        };

        function* gen(): Iterator<any> {
            let result = yield asyncFn(yield "please give me callback");
            expect(result).toBe("[async result]");
        }

        let it: Iterator<any> = gen();
        let result: any = it.next(); // yield the first yield inside the async function
        expect(result.value).toBe('please give me callback');

        it.next((res: any): any => {
            let result: any = it.next(res); // now yield the second yield, and this is where we return the callback result
            expect(result.done).toBe(true);
            done();
        });

        // how to remove generator from memory?
    })


});

