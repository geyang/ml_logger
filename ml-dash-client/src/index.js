import React from 'react';
import ReactDOM from 'react-dom';
import {modernEnvironment} from "./data";
import {BrowserProtocol, queryMiddleware} from 'farce';
import {createFarceRouter, createRender, makeRouteConfig, Route,} from 'found';
import {Resolver} from 'found-relay';
import FrontPage from './pages/FrontPage';
import Profile, {ProfileQuery, render as ProfileRender} from "./pages/Profile";
import KitchenSink from "./pages/KitchenSink";
import Dash from "./pages/Dash";
import Theme from "./Theme";
import Settings from "./pages/Settings";
import Profiles from "./pages/Profiles";
import store from "./local-storage";

const Router = createFarceRouter({
  historyProtocol: new BrowserProtocol(),
  historyMiddlewares: [queryMiddleware],
  routeConfig: makeRouteConfig(
      <Route path="/">
        <Route Component={FrontPage}/>
        <Route path="profiles" Component={Profiles}/>
        {/*<Route path="sink" Component={KitchenSink}/>*/}
        {/*<Route path="settings" Component={Settings}/>*/}
        <Route path=":username" Component={Profile}
               prepareVariables={(params) => params} query={ProfileQuery}
               render={ProfileRender}/>
        <Route path=":username/:project/:path*" Component={Dash}/>
      </Route>
  ),

  render: createRender({}),
});

if (!store.value.profile)
  if (window.location.pathname !== "/profiles")
    window.location.href = '/profiles';

ReactDOM.render(
    <Theme full={true}>
        <Router resolver={new Resolver(modernEnvironment)}/>
    </Theme>,
    document.getElementById('ml-dash'),
);

