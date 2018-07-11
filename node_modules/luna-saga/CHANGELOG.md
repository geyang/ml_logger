# Change Log

## Released

### v4.3.2 - 2017-12-22

**Important Bug Fix**
- Fix `AutoBindSubject`. A well-hidden bug. The `Saga.next` method is never called. This because the `AutoBindSubject` binds the `super.next` to `this`, instead of `this.next`. This causes the child class method `Saga.next` never to be called. Leading to `saga.value` to be `undefined`. This causes the `select` side-effect to return `undefined` state value. :star: :beers: 