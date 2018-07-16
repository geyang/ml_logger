import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter} from 'react-router-dom';
import {Route, Switch} from 'react-router';
import Experiment from "./pages/Experiment";
import {ConnectedRouter} from './model';



const Noop = (...p) => <div>noop</div>;


document.addEventListener('DOMContentLoaded', function () {
    ReactDOM.render(
        <ConnectedRouter>
            <Switch>
                <Route exact path="/" component={Experiment}/>
                <Route path="/running" component={Noop}/>
                <Route exact path="/experiments/:bucketKey" component={Experiment}/>
                <Route exact path="/experiments/:bucketKey/:experimentKey+" component={Experiment}/>
                <Route path="/chart/:bucketKey/:experimentKey+" component={Experiment}/>
            </Switch>
        </ConnectedRouter>
        , document.getElementById('root')
    );
});
// registerServiceWorker();
