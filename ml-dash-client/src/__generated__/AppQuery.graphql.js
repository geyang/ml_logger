/**
 * @flow
 * @relayHash 02ac32accc3e04488fbfc16d74f138ac
 */

/* eslint-disable */

'use strict';

/*::
import type { ConcreteRequest } from 'relay-runtime';
export type AppQueryVariables = {||};
export type AppQueryResponse = {|
  +empire: ?{|
    +id: string,
    +name: ?string,
  |},
  +rebels: ?{|
    +id: string,
    +name: ?string,
  |},
  +user: ?{|
    +username: ?string,
    +name: ?string,
  |},
|};
export type AppQuery = {|
  variables: AppQueryVariables,
  response: AppQueryResponse,
|};
*/


/*
query AppQuery {
  empire {
    id
    name
  }
  rebels {
    id
    name
  }
  user {
    username
    name
    id
  }
}
*/

const node/*: ConcreteRequest*/ = (function(){
var v0 = {
  "kind": "ScalarField",
  "alias": null,
  "name": "id",
  "args": null,
  "storageKey": null
},
v1 = {
  "kind": "ScalarField",
  "alias": null,
  "name": "name",
  "args": null,
  "storageKey": null
},
v2 = [
  (v0/*: any*/),
  (v1/*: any*/)
],
v3 = {
  "kind": "LinkedField",
  "alias": null,
  "name": "empire",
  "storageKey": null,
  "args": null,
  "concreteType": "Faction",
  "plural": false,
  "selections": (v2/*: any*/)
},
v4 = {
  "kind": "LinkedField",
  "alias": null,
  "name": "rebels",
  "storageKey": null,
  "args": null,
  "concreteType": "Faction",
  "plural": false,
  "selections": (v2/*: any*/)
},
v5 = {
  "kind": "ScalarField",
  "alias": null,
  "name": "username",
  "args": null,
  "storageKey": null
};
return {
  "kind": "Request",
  "fragment": {
    "kind": "Fragment",
    "name": "AppQuery",
    "type": "Query",
    "metadata": null,
    "argumentDefinitions": [],
    "selections": [
      (v3/*: any*/),
      (v4/*: any*/),
      {
        "kind": "LinkedField",
        "alias": null,
        "name": "user",
        "storageKey": null,
        "args": null,
        "concreteType": "User",
        "plural": false,
        "selections": [
          (v5/*: any*/),
          (v1/*: any*/)
        ]
      }
    ]
  },
  "operation": {
    "kind": "Operation",
    "name": "AppQuery",
    "argumentDefinitions": [],
    "selections": [
      (v3/*: any*/),
      (v4/*: any*/),
      {
        "kind": "LinkedField",
        "alias": null,
        "name": "user",
        "storageKey": null,
        "args": null,
        "concreteType": "User",
        "plural": false,
        "selections": [
          (v5/*: any*/),
          (v1/*: any*/),
          (v0/*: any*/)
        ]
      }
    ]
  },
  "params": {
    "operationKind": "query",
    "name": "AppQuery",
    "id": null,
    "text": "query AppQuery {\n  empire {\n    id\n    name\n  }\n  rebels {\n    id\n    name\n  }\n  user {\n    username\n    name\n    id\n  }\n}\n",
    "metadata": {}
  }
};
})();
// prettier-ignore
(node/*: any*/).hash = 'c3f54016f9836af15b1fbac48dd80701';
module.exports = node;
