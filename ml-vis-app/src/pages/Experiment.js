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
    removePath, setBucket,
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
import {
    ParameterDataContainer,
    ChartDataContainer,
    ComparisonDataContainer,
    ChartToSeries
} from "../components/ChartDataContainer";
import {ChartKeyTagInput} from "../components/chart-key-tag-input";
import VisibilitySensor from 'react-visibility-sensor';
import {Text, TextHighlight} from "../components/text-components";
import {ExperimentParameterFilter} from "../components/experiment-params-filter";
import {SrcContainer} from "../components/SrcContainer";

const FlexItemSrcContainer = styled(SrcContainer)`flex: auto 0 0`;
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
const ParamKeyStyle = styled.div`
     .ReactTags__selected {
        display: flex;
        flex-direction: row;
        > .ReactTags__tag {
            flex: auto 0 0;
            margin: 0 0;
            border-radius: 0px;
            font-size: 15px
            background-color: while;
            color: black;
            padding: 2px 4px 2px 12px;
            border-right: solid 1px black;
            a {
                padding: 4px 4px 4px 8px;
                color: black;
            }
        }
        .ReactTags__tagInput {
            margin-left: 14px;
            box-shadow: none;
        }
     }
`;


const Chart = LineChartConfidence;

class Experiment extends Component {

    componentDidMount() {
        this.props.dispatch(setBucket(this.props.match.params.bucketKey));
        this.props.dispatch(goTo("/" + (this.props.match.params.experimentKey || "")));
    }

    componentWillUpdate(nextProps) {
        if (nextProps.match.params.bucketKey !== this.props.match.params.bucketKey) {
            nextProps.dispatch(setBucket(nextProps.match.params.bucketKey));
        }
        if (nextProps.match.params.experimentKey !== this.props.match.params.experimentKey) {
            nextProps.dispatch(goTo("/" + (nextProps.match.params.experimentKey || "")));
        }
    }


    render() {
        const {
            bucket, currentDirectory, parameterKeys, paramFiles,
            searchQuery, filteredFiles = [], filteredMetricsFiles = [], filteredParamFiles = [],
            showComparison, showConfig, dispatch,
            chartKeys, yMin, yMax,
        } = this.props;

        const parentDirectory = parentDir(currentDirectory) || '/';

        return <Flex>
            <Helmet>
                <link sync href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet"/>
                <link sync href="https://unpkg.com/react-vis/dist/style.css" rel="stylesheet"/>
                <link sync href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/styles/default.min.css"
                      rel="stylesheet"/>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"/>
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
                    <Link to={uriJoin('/experiments', bucket + parentDirectory)}>go back</Link>
                    <h1>{currentDirectory}</h1>
                    {filteredFiles.map((f) =>
                        <div key={f.name}>
                            <Link to={uriJoin("/experiments", bucket + currentDirectory, f.path)}>
                                <h6>{f.name}</h6>
                            </Link>
                            <button onClick={() => dispatch(removePath(uriJoin(currentDirectory, f.path)))}/>
                        </div>
                    )}
                </div>
                <Flex column className="dash-container" style={{height: "100%"}}>
                    <DashboardHeader row className="dash-board-header">
                        <FlexItem component="div">{currentDirectory}</FlexItem>
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
                    <ParamKeyStyle><ExperimentParameterFilter/></ParamKeyStyle>
                    <FlexItem fluid style={{overflowY: "auto"}}>
                        {filteredParamFiles.map(function (f) {

                            const paramsSrc = uriJoin(currentDirectory, f.path);
                            const experimentDir = uriJoin(currentDirectory, parentDir(f.path));
                            const metricsSrc = uriJoin(experimentDir, 'metrics.pkl');
                            return <VisibilitySensor partialVisibility={true}>{
                                ({isVisible}) =>
                                    <Flex column key={f.path}>
                                        {isVisible
                                            ? <SrcContainer key='params-bar'
                                                            src={paramsSrc}
                                                            fetchCallback={() => dispatch(fetchData(paramsSrc))}>{
                                                data => data
                                                    ? <Flex row>{parameterKeys.map(k => <FlexItem
                                                        key={k}>{k + ":" + data[k]}</FlexItem>)}</Flex>
                                                    : <Flex row>{parameterKeys.map(k => <FlexItem
                                                        key={k}>{k + ": "}</FlexItem>)}</Flex>
                                            }</SrcContainer>
                                            : <div>not visible</div>}
                                        <Flex row style={{overflowX: "auto", overflowY: "hidden"}}>{
                                            isVisible
                                                ? chartKeys.map(chartKey => {
                                                    if (chartKey.match(/^video:/))
                                                        return <video key={chartKey}
                                                                      src={`http://54.71.92.65:8082/files${experimentDir}/${chartKey.slice(6)}`}
                                                                      height={150} controls playsInline={true}
                                                                      type="video/mp4"/>;
                                                    else if (chartKey.match(/^text:/))
                                                        return <Text src={`${experimentDir}/${chartKey.slice(5)}`}
                                                                     className={'diff'}
                                                                     style={{
                                                                         height: "150px",
                                                                         width: "500px",
                                                                         overflowY: "auto"
                                                                     }}/>;
                                                    else if (chartKey.match(/parameters\.pkl/))
                                                        return <table></table>
                                                    else return <FlexItemSrcContainer key={chartKey}
                                                                                      src={metricsSrc}
                                                                                      fetchCallback={() => dispatch(fetchData(metricsSrc))}
                                                        >{data => <ChartToSeries records={data} chartKey={chartKey}
                                                                                 component={LineChartConfidence}/>
                                                        }</FlexItemSrcContainer>;
                                                })
                                                : <div
                                                    style={{height: "150px"}}> placeholder <br/> placeholder <br/> placeholder <br/> placeholder <br/> =============
                                                </div>
                                        }</Flex>
                                    </Flex>
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
        const {bucketKey, currentDirectory, path, chartKeys, dispatch, children, ...props} = this.props;
        const parentDirectory = parentDir(path);
        const experimentDirectory = uriJoin(currentDirectory, parentDirectory);
        const dataPath = uriJoin(currentDirectory, path);
        return <div key={path} {...props}>
            <Flex row>
                <FlexItem fixed component={Link}
                          to={uriJoin("/experiments", bucketKey + experimentDirectory)}>
                    {parentDirectory}
                </FlexItem>
                <FlexItem component="button"
                          onClick={() => dispatch(fetchData(uriJoin(currentDirectory, path), true))}>refresh</FlexItem>
                <FlexItem component='a'
                          href={"http://54.71.92.65:8082/files" + dataPath + "?json=1&download=0"}
                          target="_blank">view json</FlexItem>
                <FlexItem component='a'
                          href={"http://54.71.92.65:8082/files" + dataPath + "?download=1"}
                          target="_blank">download pkl</FlexItem>
                <FlexItem component="button"
                          onClick={() => dispatch(removePath(experimentDirectory))}>delete experiment</FlexItem>
            </Flex>
            {children}
        </div>

    }
}


export default withRouter(selector(identity, Experiment, true));
