import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserProtocol, queryMiddleware} from 'farce';
import {createFarceRouter, createRender, makeRouteConfig, Route,} from 'found';
import {Resolver} from 'found-relay';
import {modernEnvironment} from "./data";
import App, {query} from './pages/App';
import FrontPage from './pages/FrontPage';

const Router = createFarceRouter({
  historyProtocol: new BrowserProtocol(),
  historyMiddlewares: [queryMiddleware],
  routeConfig: makeRouteConfig(
      <Route path="/">
        <Route Component={FrontPage}/>
        <Route path=":username?/:project?/:path*" query={query} Component={App}
               prepareVariables={(params) => params}/>
      </Route>
  ),

  render: createRender({}),
});

ReactDOM.render(
    <Router resolver={new Resolver(modernEnvironment)}/>,
    document.getElementById('root'),
);

