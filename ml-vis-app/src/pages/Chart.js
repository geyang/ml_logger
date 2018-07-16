import React, {Component} from "react";
import {withRouter} from "react-router";
import {Link} from "react-router-dom"
import {Flex, FlexItem} from 'layout-components';

import selector, {identity} from "../lib/react-luna";
import {goTo} from "../lib/file-api";
import Header from "./layouts/Header";

// const bucketKey = "ins-runs";
// const currentDirectory = "/2018-07-13/key_binary_cluster/ablation-test-km4-ks0.1-T_lr0.0001-actmaxTrue-Q_lr0.0001-c4-a3-gaussian0.1-sd1001-172942-956405";

class Chart extends Component {
    render() {
        const {currentDirectory, dispatch, files = [], match, ...props} = this.props;
        const {bucketKey, experimentKey} = match.params;
        console.log(match, props);
        const path = `/${experimentKey}`;
        if (currentDirectory !== path) dispatch(goTo(path));
        return <Flex>
            <Header/>
            <Link to={`/experiments/${bucketKey}/${experimentKey.slice(0, experimentKey.lastIndexOf('/'))}`}>go
                back</Link>
            <h1>Current Directory {match.params.experimentKey}</h1>
            {files.map((f, key) =>
                <Link to={`/experiments/${bucketKey}/${experimentKey}/${f.path}`} key={key}>
                    <h3>{f.name}</h3>
                </Link>
            )}
            {files.map((f, key) =>
                <Link to={`/experiments/${bucketKey}/${experimentKey}/${f.path}`} key={key}>
                    <h3>{f.name}</h3>
                </Link>
            )}
        </Flex>;
    };
}


export default withRouter(selector(identity, Chart, true));
