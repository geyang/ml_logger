import React from 'react'
import {Flex, FlexItem} from 'layout-components';
import {
    XAxis,
    YAxis,
    VerticalGridLines,
    HorizontalGridLines,
    FlexibleWidthXYPlot,
    DiscreteColorLegend,
    Crosshair,
    LineSeries,
    LineSeriesCanvas  // use this for better performance.
} from 'react-vis';
import Highlight from './highlight';
import Resizable from "re-resizable";

function nullOrUndefined(b) {
    return (typeof b === 'undefined' || b === null);
}

class LineChartConfidence extends React.Component {
    state = {
        lastDrawLocation: null,
        crosshairValues: [],
        serieses: [],
        width: 400,
        height: 200
    };

    static defaultProps = {
        serieses: [],
        legendWidth: null
    };

    componentWillMount() {
        const {serieses = []} = this.props;
        this.setState({serieses: serieses.map(l => ({...l}))})
    }

    componentWillReceiveProps(nextProps) {
        const {serieses = []} = nextProps;
        if (serieses !== this.props.serieses)
            this.setState({serieses: serieses.map(l => ({...l}))});
    }

    itemClick = (item, index) => {
        const {serieses} = this.state;
        item.disabled = !item.disabled;
        this.setState({serieses});
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
    onResize = (e, direction, ref, d) => {
        this.setState({
            width: this.state.width + d.width,
            height: this.state.height + d.height,
        });
    };

    render() {
        const {serieses, lastDrawLocation} = this.state;
        let {legendWidth, xMin, xMax, yMin, yMax, ...props} = this.props;
        delete props.serieses;

        if (nullOrUndefined(yMin) || nullOrUndefined(yMax)) {
            let minMax = serieses.map(line => {
                let ys = line.data.map(({y}) => y);
                return {
                    max: Math.max(...ys),
                    min: Math.min(...ys)
                }
            });
            if (nullOrUndefined(yMin)) yMin = Math.min(...minMax.map(({min}) => min));
            if (nullOrUndefined(yMax)) yMax = Math.max(...minMax.map(({max}) => max));
        }

        return (
            <Flex row {...props} justify={'stretch'} style={{minHeight: "150px"}}
            >
                <FlexItem component={Resizable}
                          size={{width: this.state.width, height: this.state.height}}
                          onResizeStop={this.onResize}
                          style={{overflowY: "hidden", overflowX: "hidden"}}
                          handleStyles={{
                              right: {background: 'linear-gradient(to top, rgba(1, 0, 0, 0.2), transparent 15px, transparent 100%)'},
                              bottom: {background: 'linear-gradient(to left, rgba(1, 0, 0, 0.2), transparent 15px, transparent 100%) '},
                          }}
                >
                    <FlexibleWidthXYPlot
                        className="chart no-select"
                        animation
                        xDomain={lastDrawLocation && [lastDrawLocation.left, lastDrawLocation.right]}
                        yDomain={[yMin, yMax]}
                        height={this.state.height}
                        width={this.state.width}
                        onMouseLeave={this.onMouseLeave}>
                        <HorizontalGridLines/>
                        <YAxis/>
                        <XAxis/>
                        {serieses.map((line) =>
                            <LineSeries key={line.title} data={line.disabled ? [] : line.data}
                                        onNearestX={this.onNearestX(line.title)}
                            />)}
                        <Crosshair values={this.state.crosshairValues}/>
                        <Highlight onBrushEnd={this.onBrushEnd}/>
                    </FlexibleWidthXYPlot>
                </FlexItem>
                <FlexItem style={{overflowY: 'auto', overflowX: "hidden"}} height={this.state.height}>
                    <DiscreteColorLegend width={legendWidth} items={serieses} onItemClick={this.itemClick}/>
                </FlexItem>
            </Flex>
        )
    }
}

const ResizableXYPlot = ({style, size, onResizeStart, onResizeStop}) => {
    return <Resizable style={style} size={size} onResizeStart={onResizeStart}
                      onResizeStop={onResizeStop}><FlexibleWidthXYPlot/>
    </Resizable>;
};

export default LineChartConfidence;
