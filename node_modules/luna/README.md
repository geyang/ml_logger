# Luna, a reactive redux library with built-in support for async action creator and Thunks

[![Join the chat at https://gitter.im/escherpad/luna](https://img.shields.io/badge/GITTER-join%20chat-green.svg?style=flat-square)](https://gitter.im/escherpad/luna?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Luna is a reactive redux implementation based on the Reactive-Extension (Rxjs@v5.0-beta) and build with Typescript. Luna try to improve upon existing implementations of redux by providing out of the box support for async actions, ways to access child components of the root store as a stream and more. Luna drops verbatim compatibility with the original `redux` to give rise to a more coherent, reactive API.

## Features
1. **Luna `store$` object is reactive**. You can subscribe to it and use all of `rxjs`'s operators, such as `debounceTime`, `throttleTime`, `map`, `flatMap`, `buffer` etc.
2. Luna `dispatch` function takes in both `thunk`s and `action`. As well as a batch(array) of thunks and actions, and update the store state in a single batch. Since dispatching and rendering in react are synchronous

## Installing Luna

Just do `npm install luna` to install from npm. Or you can install from github:

```shell
npm install luna@git+https://git@github.com/escherpad/luna.git 
```

## To Use:

```javascript
import {Store} from "luna";

let reducer = function (state = 0, action){// default value here would be 0.
    if (action.type === "INC") {
        return state + 1;
    } else {
        return state;
    }
}

let store$ = new Store(reducer);

store$.dispatch({type: "INC"})
store$.subscribe((state)=>console.log(state));
// 0
// 1
```

## The `store` instance

calling `new Store(reducer[, initialState])` returns a `store$` instance. Luna `Store` is a subclass of the BehaviorSubject from rx. So it takes an intialstate at instantiation, and emits a stream of state objects that you can subscribe to. 

the `store$.action$` is a (publish) subject for the actions. The store internally subscribes to this stream and executes the reducers on the store state in response to events from this action stream. Because it is a (publish) subject, it does not trigger event on subscription. It also does not have the `getValue()` method.  

The `store$.update$` is a (publish) subject for `{state, action}` bundle. It receives updated state/action bundle after the action has been applied to the store. This stream is used as a `post-action` hook for middlewares such as [luna-saga](https://github.com/escherpad/luna-saga). Because it is a (publish) subject, it does not trigger event on subscription. It also does not have the `getValue()` method.

## Wanna use Reactive-Extention (Rxjs) and redux in your project, but don't know how?

Luna is the easiest way to get started. 

Redux is a very simple library with a small API footprint. It is written without taking advantage of the Reactive-Extension. Now using Rxjs as the message/middleware layer, we make redux even more powerful and natural to use. Luna is written with redux's spirit and design pattern in mind, but it includes all of the different parts in one place, and make it easy to start developing in a redux-like way right away. Luna replaces `redux`, `redux-thunk`, `redux-middleware`, and allows you to use asynchronous `actionCreators` directly in the dispatcher.

### Start by Designing Your Store Tree

For an application, Redux provides a single data store for the entire application. To architect your app, you first start with designing the structure of the store object. Then you can write reducers for those sub-part of the root store, and use the `combineReducer` function to combine those into the root reducer. 

### `map =>` Array Composition Pattern

To deal with arrays (collections of documents for instance), you use the array composition pattern. Dan has a very nice vieo on Egghead.io \([link](https://egghead.io/lessons/javascript-redux-reducer-composition-with-arrays)\)


### `()=>` Action Creator Pattern

Another useful patter is action creators. You write a simple function that returns an action object. \([link: action creators](https://egghead.io/lessons/javascript-redux-extracting-action-creators)\)

### `Thunk` and Async Actions 

**Note: Async Action is going to be deprecated.**

Now what about async operations such as network calls? Redux thinks that the `store` object should only be mutated synchronously. This makes everything easier to understand and sequential. To allow async operations, you then rely on a concept called 'thunk'. In simple words, because action objects are not enough, you dispatch functions that contains a certain execution context. With redux you need to use the `redux-thunk` middleware. It patches the redux `store` class, and makes the dispatch method accept `thunks`. This sytanx is slightly strange, so with Luna I decided to support dispatching `thunks` out of the box and avoid the monkey patching.

### Middlewares (don't need anymore)

You don't need middleware anymore now you have Rxjs. In Rxjs, an observable is a stream of data that you can subscribe to. In Luna, the `Store` is a subclass of the `Rxjs.BehaviorSubject`, which is an extension of the `Observable` class. In addition, Luna `Store` also has a property called `Store.action$`, which is a `Rx.Subject` for all of the actions the store accepts. In a reactive paradigm, if you want to log all of the actions for instance, you can just subscribe to the `Store.action$` stream.

### Persistent Storage and Children of the Root Store

Luna also provides a convenient method called `Store.select`. It allows you to pass in the key of a child of the root store object, and returns a stream for that child part of the model. 

Therefore, if you have an app, and you want to save only part of the app state in the localStorage, you can just do the following:

```typescript
interface State {
    loginSession: User,
    notes: Note[],
    otherData: Blah...
}

const rootReducer:Reducer<State> = {
    loginSession: loginSessionReducer,
    notes: notesReducer,
    ...
}

const initialState:State = {
    loginSession: [],
    notes: [],
    ...
}

var store = new Store(rootReducer, intialState);

// To save the loginSession in the localStorage of the 
// browser, you can just subscribe like this:

store
    .select('loginSession')
    .subscribe(loginSession => {
        window.localStorage.setItem('loginSession', loginSession);
    })
```
example here: [line in test file](https://github.com/escherpad/luna/commit/e0741cc4ca8af2ad4d3a38e08c5681838f342ed4#diff-6b623d6bcf5e7f06c466aa060ec9c4b6R279)

and I personally find this very powerful!


## About this library and What's different about Luna (from redux)?

- Luna is written using the reactive-extension, so that both the state of the store and the actions are streams.
- Luna `dispatch` method supports `actionCreator` and asynchronous actions out of the box.
    - Luna's `Thunks` take no input arguments. The Store object is accessed as `this` keyword in the thunk. I'm experimenting with this as a cleaner syntax.
- Luna is written for an Angular2 project, and provide dependency injection (DI) via a 'provideStore' 
    function, and a StoreService class that you can extend in your angular2 applications.
    
## For Angular2 Developers Out There~

Angular2 Beta just came out, and a lot of us are still figuring out the best practices. Getting redux, Typescript and angular2 dependency injection to work well together was a challenge. 

To make getting started easy for you, Luna includes a simple class called `StoreService` in Luna. In escherpad the application I'm working on, Each child of the root store has a store service class that extends `StoreService` class. This service class include the reducer, action types, as well as the action creators inside, and use the angular2 dependency injection to connect everything together.

This way, script for each child store only need to know what it depends on itself. Components become truly composable.

I currently do not use the `provideStore` provider for the reason given above.

## Developing Luna

- you need to have `karma-cli` installed globally. (do `npm install -g karma-cli`)
- to build, run `npm run build`. This just calls `tsc` in project root.
- to test, you can use `karma start`. I use webStorm's karma integration to run the tests.

```typescript
/** Created by ge on 12/6/15. */
import {Action, Hash, Reducer} from "luna";

// the Stat interface need to extend Hash so that the index keys are available.
interface TestState extends Hash {
    counter:number;
}

// Reducer example
const reducer = <Reducer>function (state:TestState, action:Action<TestState>, callback:(state:TestState)=>void):TestState {
    if (action.type === "INC") {
        state.counter += 1;
        return state
    } else if (action.type === "DEC") {
        state.counter -= 1;
        return state
    } else {
        return state;
    }
};

// define the initial state of store
var state:TestState = {
    counter: 20
};

// now create store
var store = new Store<TestState>(reducer, state);

// stream states to view
store.subscribe(
    (state)=> {
        console.log('spec state: ', state)
    },
    error=> console.log('error ', error),
    () => {
        console.log('completed.');
        done();
    }
);

// dispatch actions using the dispatcher$ BehaviorSubject
var action = {
    type: "INC"
}
store.dispatcher$.next(action);

```

## Luna's different signature for asynchronous actions

Here is the syntax with redux-thunk:

```typescript
// But what do you do when you need to start an asynchronous action,
// such as an API call, or a router transition?

// Meet thunks.
// A thunk is a function that returns a function.
// This is a thunk.

function makeASandwichWithSecretSauce(forPerson) {

  // Invert control!
  // Return a function that accepts `dispatch` so we can dispatch later.
  // Thunk middleware knows how to turn thunk async actions into actions.

  return function (dispatch) {
    return fetchSecretSauce().then(
      sauce => dispatch(makeASandwich(forPerson, sauce)),
      error => dispatch(apologize('The Sandwich Shop', forPerson, error))
    );
  };
}

// Thunk middleware lets me dispatch thunk async actions
// as if they were actions!

store.dispatch(
  makeASandwichWithSecretSauce('Me')
);
```

The signature for the returned thunk has `dispatch` and `getValue`. I find this signature kind of arbitrary. Here with Luna, you can do:

```typescript
// But what do you do when you need to start an asynchronous action,
// such as an API call, or a router transition?

// Meet thunks.
// A thunk is a function that returns a function.
// This is a thunk.

function makeASandwichWithSecretSauce(forPerson) {

  // Invert control!
  // Return a function that accepts `dispatch` so we can dispatch later.
  // Thunk middleware knows how to turn thunk async actions into actions.

  return function () {
    var _store = this;
    return fetchSecretSauce().then(
      sauce => _store.dispatch(makeASandwich(forPerson, sauce)),
      error => _store.dispatch(apologize('The Sandwich Shop', forPerson, error))
    );
  };
}

// Thunk middleware lets me dispatch thunk async actions
// as if they were actions!

store.dispatch(
  makeASandwichWithSecretSauce('Me')
);
```

## Plans next

Personally I think documentation is the most important part of a library, and for making everyone's life easier. Bad documentation wastes people's time.

If you would like to help, besides code you can create even larger impact by writing up examples. Redux (and luna) is a simple idea. Let's make it easier for people to understand the concept and start doing things that they set-out to do asap.

### Todo List

- [ ] use immutable in the test instead. Current form is too sloppy!
- [ ] more testing cases with complicated stores
- better store life-cycle support

## Acknowledgement

This library is influenced by @jas-chen's work on redux-core, and received help from @fxck and @robwormald.

Luna is part of my effort on re-writting [escherpad](http://www.escherpad.com), a beautiful real-time collaborative notebook supporting real-time LaTeX, collaborative Jupyter notebook, and a WYSIWYG rich-text editor.

## About Ge

I'm a graduate student studying quantum information and quantum computer at University of Chicago. When I'm not tolling away in a cleanroom or working on experiments, I write `(java|type)script` to relax. You can find my publications here: [google scholar](https://scholar.google.com/citations?user=vaQcF6kAAAAJ&hl=en)

## LICENSING

MIT.
