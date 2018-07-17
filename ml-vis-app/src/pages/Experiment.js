import React, {Component} from "react";
import {withRouter} from "react-router";
import {Link} from "react-router-dom"
import {Flex, FlexItem} from 'layout-components';
import selector, {identity} from "../lib/react-luna";
import {goTo, parentDir, queryInput, removePath} from "../lib/file-api";
import Header from "./layouts/Header";
import LineChartConfidence from "../components/LineChartConfidence";
import {Helmet} from 'react-helmet';
import {uriJoin} from '../lib/file-api';
import SplitPane from "react-split-pane";
import styled from "styled-components";
import ChartDataContainer from "../components/ChartDataContainer";

const FlexItemChartContainer = styled(ChartDataContainer)`flex: auto 0 0`;

class Experiment extends Component {
    state = {
        compare: false
    };

    constructor(props) {
        super(props);
        const {currentDirectory, dispatch, match: {params: {bucketKey, experimentKey = ""}}} = props;
        dispatch(goTo("/" + experimentKey));
    }

    static getDerivedStateFromProps(props) {
        const {currentDirectory, dispatch, match: {params: {bucketKey, experimentKey = ""}}} = props;
        if (currentDirectory !== "/" + experimentKey) dispatch(goTo("/" + experimentKey));
        return {}
    }

    toggleComparison = () => this.setState({compare: !this.state.compare});

    render() {
        const {
            currentDirectory, searchQuery, files, metrics, dispatch,
            chartKeys,
            match: {params: {bucketKey, experimentKey = ""}}, location, history, ...props
        } = this.props;
        const {compare} = this.state;

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
                <title>Escher.ml</title>
            </Helmet>
            <SplitPane minSize={50} defaultSize={300}
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
                        back</Link>
                    <h1>{experimentKey}</h1>
                    {filteredFiles.map((f) =>
                        <div key={f.name}>
                            <Link to={uriJoin("/experiments", bucketKey, experimentKey, f.path)}>
                                <h6>{f.name}</h6>
                            </Link>
                            <button onClick={() => dispatch(removePath(uriJoin(experimentKey, f.path)))}/>
                        </div>
                    )}
                </div>
                <div className="dash-container">
                    <Flex row className="dash-board-header">
                        <FlexItem component="div">{experimentKey}</FlexItem>
                        <FlexItem component="button" onClick={this.toggleComparison}>compare</FlexItem>
                    </Flex>
                    {filteredMetricFiles.map((f) =>
                        <ExperimentRow key={f.path}
                                       bucketKey={bucketKey} experimentKey={experimentKey} path={f.path}
                                       chartKeys={chartKeys} dispatch={dispatch}
                        >{
                            chartKeys.map(chartKey =>
                                <FlexItemChartContainer
                                    key={chartKey}
                                    component={LineChartConfidence}
                                    dataKey={uriJoin(currentDirectory, f.path)}
                                    chartKey={chartKey}/>)
                        }</ExperimentRow>
                    )}
                </div>
            </SplitPane>
        </Flex>;
    };
}


function ExperimentRow({bucketKey, experimentKey, path, chartKeys, dispatch, children}) {
    const parentDirectory = parentDir(path);
    const experimentDirectory = uriJoin(experimentKey, parentDirectory);
    const dataPath = uriJoin(experimentKey, path);
    return <div key={path}>
        <Flex row>
            <FlexItem fixed component={Link}
                      to={uriJoin("/experiments", bucketKey, experimentDirectory)}>
                {parentDirectory}
            </FlexItem>
            <FlexItem component="button"
                      onClick={() => dispatch(removePath(experimentDirectory))}>delete
                experiment</FlexItem>
            <FlexItem component='a'
                      href={uriJoin("http://54.71.92.65:8082/files", dataPath + "?json=1&download=0")}
                      target="_blank">view json</FlexItem>
            <FlexItem component='a'
                      href={uriJoin("http://54.71.92.65:8082/files", dataPath + "?download=1")}
                      target="_blank">download pkl</FlexItem>
        </Flex>
        <Flex row style={{overflowX: "auto"}}>
            {children}
        </Flex>
    </div>

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
