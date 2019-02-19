/**
 * @flow
 * @relayHash 39e9f3d2ec6ca737377a6d0ffed07a94
 */

/* eslint-disable */

'use strict';

/*::
import type { ConcreteRequest } from 'relay-runtime';
export type AppQueryVariables = {|
  username?: ?string
|};
export type AppQueryResponse = {|
  +user: ?{|
    +username: ?string,
    +name: ?string,
  |}
|};
export type AppQuery = {|
  variables: AppQueryVariables,
  response: AppQueryResponse,
|};
*/


/*
query AppQuery(
  $username: String
) {
  user(username: $username) {
    username
    name
    id
  }
}
*/

const node/*: ConcreteRequest*/ = (function(){
var v0 = [
  {
    "kind": "LocalArgument",
    "name": "username",
    "type": "String",
    "defaultValue": null
  }
],
v1 = [
  {
    "kind": "Variable",
    "name": "username",
    "variableName": "username",
    "type": "String"
  }
],
v2 = {
  "kind": "ScalarField",
  "alias": null,
  "name": "username",
  "args": null,
  "storageKey": null
},
v3 = {
  "kind": "ScalarField",
  "alias": null,
  "name": "name",
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
    "argumentDefinitions": (v0/*: any*/),
    "selections": [
      {
        "kind": "LinkedField",
        "alias": null,
        "name": "user",
        "storageKey": null,
        "args": (v1/*: any*/),
        "concreteType": "User",
        "plural": false,
        "selections": [
          (v2/*: any*/),
          (v3/*: any*/)
        ]
      }
    ]
  },
  "operation": {
    "kind": "Operation",
    "name": "AppQuery",
    "argumentDefinitions": (v0/*: any*/),
    "selections": [
      {
        "kind": "LinkedField",
        "alias": null,
        "name": "user",
        "storageKey": null,
        "args": (v1/*: any*/),
        "concreteType": "User",
        "plural": false,
        "selections": [
          (v2/*: any*/),
          (v3/*: any*/),
          {
            "kind": "ScalarField",
            "alias": null,
            "name": "id",
            "args": null,
            "storageKey": null
          }
        ]
      }
    ]
  },
  "params": {
    "operationKind": "query",
    "name": "AppQuery",
    "id": null,
    "text": "query AppQuery(\n  $username: String\n) {\n  user(username: $username) {\n    username\n    name\n    id\n  }\n}\n",
    "metadata": {}
  }
};
})();
// prettier-ignore
(node/*: any*/).hash = '4b88f2358f09103af89ca8b11ef2bb51';
module.exports = node;
