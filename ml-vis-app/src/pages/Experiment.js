import React, {Component} from "react";
import {withRouter} from "react-router";
import {Link} from "react-router-dom"
import {Flex, FlexItem, FlexSpacer} from 'layout-components';
import selector, {identity} from "../lib/react-luna";
import {
    fetchData,
    goTo, markDirty,
    parentDir,
    queryInput,
    removePath,
    setYMax,
    setYMin,
    toggleComparison,
    toggleConfig
} from "../lib/file-api";
import Header from "./layouts/Header";
import LineChartConfidence from "../components/LineChartConfidence";
import {Helmet} from 'react-helmet';
import {uriJoin} from '../lib/file-api';
import SplitPane from "react-split-pane";
import styled from "styled-components";
import {ChartDataContainer, ComparisonDataContainer} from "../components/ChartDataContainer";
import {ChartKeyTagInput} from "../components/chart-key-tag-input";
import VisibilitySensor from 'react-visibility-sensor';

const FlexItemChartContainer = styled(ChartDataContainer)`flex: auto 0 0`;
const FlexItemComparisonContainer = styled(ComparisonDataContainer)`flex: auto 0 0`;
const DashboardHeader = styled(Flex)`
    padding: 10px 0;
    border-bottom: 1px solid #e6e6e6;
    flex: auto 0 0;
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


const Chart = LineChartConfidence;

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
            currentDirectory, searchQuery, filteredFiles, filteredMetricsFiles, showComparison, showConfig, dispatch,
            chartKeys, yMin, yMax,
            match: {params: {bucketKey, experimentKey = ""}}, location, history, ...props
        } = this.props;
        console.log(filteredMetricsFiles);

        return <Flex>
            <Helmet>
                <link sync href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet"/>
                <link sync href="https://unpkg.com/react-vis/dist/style.css" rel="stylesheet"/>
                <style>{"body {font-family: 'lato'; margin: 0}"}</style>
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
                <Flex column className="dash-container" style={{height: "100%"}}>
                    <DashboardHeader row className="dash-board-header">
                        <FlexItem component="div">{experimentKey}</FlexItem>
                        <TagInputStyle><ChartKeyTagInput/></TagInputStyle>
                        <FlexItem component="button" onClick={() => dispatch(toggleComparison())}>compare</FlexItem>
                        <FlexSpacer/>
                    </DashboardHeader>
                    {showComparison ?
                        <FlexItem>
                            <Flex row align='center'>
                                <FlexItem component={'h3'}>Comparisons</FlexItem>
                                <FlexItem component={'button'} style={{margin: "0 10px"}}
                                          height={20} onClick={() => dispatch(toggleConfig())}>configure
                                </FlexItem>
                                {showConfig ?
                                    <FlexItem>
                                        y min
                                        <input value={yMin} onInput={(e) => dispatch(setYMin(e.target.value || null))}
                                               style={{width: "5em"}} type={'number'}/>
                                        max
                                        <input value={yMax} onInput={(e) => dispatch(setYMax(e.target.value || null))}
                                               style={{width: "5em"}} type={'number'}/>
                                    </FlexItem>
                                    : null
                                }
                            </Flex>
                            <Flex row style={{overflowX: "auto"}}>
                                {chartKeys.map(chartKey =>
                                    <FlexItemComparisonContainer
                                        dispatch={dispatch}
                                        key={chartKey}
                                        component={Chart}
                                        yMin={yMin}
                                        yMax={yMax}
                                        dataKeys={filteredMetricsFiles.map(f => uriJoin(currentDirectory, f.path))}
                                        chartKey={chartKey}
                                        legendWidth={null}
                                    />)}
                            </Flex>

                        </FlexItem>
                        : null
                    }
                    <FlexItem component={'h3'}>Experiments</FlexItem>
                    <FlexItem fluid style={{overflowY: "auto"}}>
                        {filteredMetricsFiles.map(f => {
                            const dataKey = uriJoin(currentDirectory, f.path);
                            return <VisibilitySensor partialVisibility={true}>{
                                ({isVisible}) =>
                                    <ExperimentRow key={f.path}
                                                   bucketKey={bucketKey}
                                                   experimentKey={experimentKey}
                                                   path={f.path}
                                                   chartKeys={chartKeys}
                                                   dispatch={dispatch}
                                                   currentDirectory={currentDirectory}>
                                        {isVisible
                                            ? chartKeys.map(chartKey =>
                                                chartKey.match("video:")
                                                    ? <video
                                                        src={`http://54.71.92.65:8082/files/${experimentKey}/${chartKey.slice(5)}`}
                                                        height={150} controls/>
                                                    : <FlexItemChartContainer
                                                        dispatch={dispatch}
                                                        fetchCallback={(dataKey) => dispatch(fetchData(dataKey))}
                                                        key={chartKey}
                                                        component={LineChartConfidence}
                                                        dataKey={dataKey}
                                                        chartKey={chartKey}/>)
                                            : <div style={{height: "150px"}}> placeholder <br/> placeholder <br/> placeholder <br/> placeholder <br/> ============= </div>
                                        } </ExperimentRow>
                            }</VisibilitySensor>
                        })}
                    </FlexItem>
                </Flex>
            </SplitPane>
        </Flex>;
    };
}


class ExperimentRow extends Component {
    state = {};

    render() {
        const {bucketKey, experimentKey, path, chartKeys, dispatch, children, currentDirectory, ...props} = this.props;
        const parentDirectory = parentDir(path);
        const experimentDirectory = uriJoin(experimentKey, parentDirectory);
        const dataPath = uriJoin(experimentKey, path);
        return <div key={path} {...props}>
            <Flex row>
                <FlexItem fixed component={Link}
                          to={uriJoin("/experiments", bucketKey, experimentDirectory)}>
                    {parentDirectory}
                </FlexItem>
                <FlexItem component="button"
                          onClick={() => dispatch(fetchData(uriJoin(currentDirectory, path)))}>refresh</FlexItem>
                <FlexItem component='a'
                          href={uriJoin("http://54.71.92.65:8082/files", dataPath + "?json=1&download=0")}
                          target="_blank">view json</FlexItem>
                <FlexItem component='a'
                          href={uriJoin("http://54.71.92.65:8082/files", dataPath + "?download=1")}
                          target="_blank">download pkl</FlexItem>
                <FlexItem component="button"
                          onClick={() => dispatch(removePath(experimentDirectory))}>delete experiment</FlexItem>
            </Flex>
            <Flex row style={{overflowX: "auto", overflowY: "hidden"}}>
                {children}
            </Flex>
        </div>

    }
}


export default withRouter(selector(identity, Experiment, true));
