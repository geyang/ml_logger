import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserProtocol, queryMiddleware} from 'farce';
import {createFarceRouter, createRender, makeRouteConfig, Route,} from 'found';
import {Resolver} from 'found-relay';
import {modernEnvironment} from "./data";
import FrontPage from './pages/FrontPage';
import Profile, {ProfileQuery} from "./pages/Profile";
import Dash, {DashPrepareVariables, DashQuery} from "./pages/Dash";
import Theme from "./Theme";

const Router = createFarceRouter({
  historyProtocol: new BrowserProtocol(),
  historyMiddlewares: [queryMiddleware],
  routeConfig: makeRouteConfig(
      <Route path="/">
        <Route Component={FrontPage}/>
        <Route path=":username" Component={Profile} prepareVariables={(params) => params} query={ProfileQuery}/>
        <Route path=":username/:project/:path*"
               Component={Dash}
               query={DashQuery}
               prepareVariables={DashPrepareVariables}/>
      </Route>
  ),

  render: createRender({}),
});

ReactDOM.render(
    <Theme full={true}>
      <Router resolver={new Resolver(modernEnvironment)}/>
    </Theme>,
    document.getElementById('root'),
);

