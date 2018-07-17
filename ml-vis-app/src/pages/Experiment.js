import React, {Component} from "react";
import {withRouter} from "react-router";
import {Link} from "react-router-dom"
import {Flex, FlexItem} from 'layout-components';
import selector, {identity} from "../lib/react-luna";
import {goTo, parentDir, queryInput, removePath, toggleComparison} from "../lib/file-api";
import Header from "./layouts/Header";
import LineChartConfidence from "../components/LineChartConfidence";
import {Helmet} from 'react-helmet';
import {uriJoin} from '../lib/file-api';
import SplitPane from "react-split-pane";
import styled from "styled-components";
import {ChartDataContainer, ComparisonDataContainer} from "../components/ChartDataContainer";
import {ChartKeyTagInput} from "../components/chart-key-tag-input";

const FlexItemChartContainer = styled(ChartDataContainer)`flex: auto 0 0`;
const FlexItemComparisonContainer = styled(ComparisonDataContainer)`flex: auto 0 0`;
const DashboardHeader = styled(Flex)`
    padding: 10px 0;
    border-bottom: 1px solid #e6e6e6;
`;
const TagInputStyle = styled.div`
     .ReactTags__selected {
        display: flex;
        flex-direction: row;
        > .ReactTags__tag {
            flex: auto 0 0;
            margin: 0 5px;
            border-radius: 14px;
            font-size: 12px
            background-color: #23aaff
            color: white;
            padding: 2px 4px 2px 10px;
            a {
                padding: 4px 4px 6px 4px;
                color: rgba(255, 255, 255, 0.7);
            }
        }
        .ReactTags__tagInput {
        }
     }
`;

class Experiment extends Component {

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

    render() {
        const {
            currentDirectory, searchQuery, files, metrics, showComparison, dispatch,
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
                    <input onInput={(e) => dispatch(queryInput(e.target.value))} value={searchQuery}/>
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
                    <DashboardHeader row className="dash-board-header">
                        <FlexItem component="div">{experimentKey}</FlexItem>
                        <TagInputStyle><ChartKeyTagInput/></TagInputStyle>
                        <FlexItem component="button" onClick={() => dispatch(toggleComparison())}>compare</FlexItem>
                    </DashboardHeader>
                    {showComparison ?
                        <div>
                            <h3>Comparisons</h3>
                            <Flex row style={{overflowX: "auto"}}>
                                {chartKeys.map(chartKey =>
                                    <FlexItemComparisonContainer
                                        key={chartKey}
                                        component={LineChartConfidence}
                                        dataKeys={filteredMetricFiles.map(f => uriJoin(currentDirectory, f.path))}
                                        chartKey={chartKey}
                                        legendWidth={null}
                                    />)}

                            </Flex>

                        </div>
                        : null
                    }
                    <div>
                        <h3>Experiments</h3>
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
