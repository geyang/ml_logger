import React from 'react'
import {Flex, FlexItem} from 'layout-components';
import {
    XAxis,
    YAxis,
    VerticalGridLines,
    HorizontalGridLines,
    FlexibleWidthXYPlot, DiscreteColorLegend, Crosshair,
    LineSeries,
    LineSeriesCanvas  // use this for better performance.
} from 'react-vis';
import {recordsToSeries} from "../data-helpers";
import Highlight from "./highlight";
import {fileApi} from "../lib/file-api";

export default class AreaChartConfidence extends React.Component {
    state = {
        src: null,
        lastDrawLocation: null,
        series: recordsToSeries([]),
        crosshairValues: []
    };

    constructor(props, context) {
        super(props, context);
    }

    componentWillMount() {
        const {src} = this.props;
        console.log(src);
        if (src) {
            fileApi.getMetricData(src).then((series) => this.setState({series}))
        }
    }

    itemClick = (item, index) => {
        const {series} = this.state;
        item.disabled = !item.disabled;
        this.setState({series});
    };
    onMouseLeave = () => this.setState({crosshairValues: []});
    onNearestX = (lineKey) => (value, n) => {
        const {crosshairValues} = this.state;
        const lineIndex = crosshairValues.findIndex(({lineKey: _lineKey}) => _lineKey === lineKey);
        if (lineIndex > -1) {
            crosshairValues[lineIndex] = {...value, lineKey};
        } else {
            crosshairValues.push({...value, lineKey});
        }
        this.setState({crosshairValues})
    };
    onBrushEnd = (area) => this.setState({lastDrawLocation: area});

    render() {
        const {series, lastDrawLocation, seriesKeys} = this.state;
        return (
            <Flex row>
                <FlexItem>
                    <FlexibleWidthXYPlot
                        animation
                        xDomain={lastDrawLocation && [lastDrawLocation.left, lastDrawLocation.right]}
                        width={400}
                        height={200}
                        onMouseLeave={this.onMouseLeave}
                    >
                        <VerticalGridLines/>
                        <HorizontalGridLines/>
                        <XAxis/>
                        <YAxis/>
                        {series.filter(line => !line.disabled).map((line) =>
                            <LineSeries key={line.title} data={line.data} onNearestX={this.onNearestX(line.title)}/>)}
                        <Highlight onBrushEnd={this.onBrushEnd}/>
                        <Crosshair values={this.state.crosshairValues}/>
                    </FlexibleWidthXYPlot>
                </FlexItem>
                <FlexItem style={{overflowY: 'auto'}} height={200}>
                    <DiscreteColorLegend width={180} items={series} onItemClick={this.itemClick}/>
                </FlexItem>
            </Flex>
        )
    }
}
