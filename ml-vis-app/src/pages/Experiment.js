import React, {Component} from "react";
import {withRouter} from "react-router";
import {Link} from "react-router-dom"
import {Flex, FlexItem} from 'layout-components';
import {parse, stringify} from "query-string";
import micromatch from "micromatch";
import selector, {identity} from "../lib/react-luna";
import {goTo, parentDir, queryInput, removePath} from "../lib/file-api";
import Header from "./layouts/Header";
import LineChartConfidence from "../components/LineChartConfidence";
import {Helmet} from 'react-helmet';
import {uriJoin} from '../lib/file-api';
import SplitPane from "react-split-pane";

class Experiment extends Component {

    constructor(props) {
        super(props);
        const {currentDirectory, dispatch, match: {params: {bucketKey, experimentKey = ""}}} = props;
        console.log(bucketKey);
        console.log([experimentKey, currentDirectory]);
        dispatch(goTo("/" + experimentKey));
    }

    static getDerivedStateFromProps(props) {
        const {currentDirectory, dispatch, match: {params: {bucketKey, experimentKey = ""}}} = props;
        console.log(bucketKey);
        console.log([experimentKey, currentDirectory]);
        if (currentDirectory !== "/" + experimentKey) dispatch(goTo("/" + experimentKey));
    }


    render() {
        const {currentDirectory, searchQuery, files, metrics, dispatch,
            match: {params: {bucketKey, experimentKey = ""}}, location, history, ...props} = this.props;


        console.log(currentDirectory, searchQuery, files, metrics);
        let filteredMetricFiles;
        try {
            filteredMetricFiles = metrics.filter(f => uriJoin(currentDirectory, f.path).indexOf(searchQuery) > -1);
        } catch (e) {
            console.error(e);
            filteredMetricFiles = [];
        }
        let filteredFiles;
        try {
            filteredFiles = files.filter(f => uriJoin(currentDirectory, f.path).indexOf(searchQuery) > -1);
        } catch (e) {
            console.error(e);
            filteredFiles = [];
        }
        return <Flex>
            <Helmet>
                <link sync href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet"/>
                <link sync href="https://unpkg.com/react-vis/dist/style.css" rel="stylesheet"/>
                <style>{"body {font-family: 'lato'; "}</style>
            </Helmet>
            <SplitPane minSize={50} defaultSize={400}
                       resizerStyle={{
                           backgroundColor: "transparent",
                           width: "10px",
                           boxSizing: "border-box",
                           borderRight: "solid 1px red",
                           marginRight: "10px"
                       }}
                       pane1Style={{overflowY: "auto"}}
                       pane2Style={{overflowY: "auto"}}
            >
                <div>
                    <Header/>
                    <input onInput={(e) => dispatch(queryInput(e.target.value))}/>
                    <Link
                        to={uriJoin('/experiments', bucketKey, parentDir(experimentKey))}>go
                        back</Link><h1>{experimentKey}</h1>
                    {filteredFiles.map((f) =>
                        <div key={f.name}>
                            <Link to={uriJoin("/experiments", bucketKey, experimentKey, f.path)}>
                                <h6>{f.name}</h6>
                            </Link>
                            <button onClick={() => dispatch(removePath(uriJoin(experimentKey, f.path)))}/>
                        </div>
                    )}
                </div>
                <div>
                    {filteredMetricFiles.map((f) =>
                        <div key={f.path}>
                            <Link to={uriJoin("/experiments", bucketKey, experimentKey, f.path)}>
                                <h6>{f.path}</h6>
                            </Link>
                            <LineChartConfidence src={uriJoin(experimentKey, `${f.path}?json=1`)}/>
                        </div>)}
                </div>
            </SplitPane>
        </Flex>;
    };
}


export default withRouter(selector(identity, Experiment, true));
// {filteredImageFiles.map((f) =>
//     <div key={f.path}>
//         <Link to={uriJoin("/experiments", bucketKey, experimentKey, f.path)}>
//             <h3>{f.path}</h3>
//             <img
//                 src={uriJoin("http://54.71.92.65:8082/files", experimentKey, `${f.path}?download=0`)}/>
//         </Link>
//     </div>)}
