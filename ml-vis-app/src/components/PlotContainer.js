import React from 'react'
import {Flex, FlexItem} from 'layout-components';

export default class PlotContainer extends React.Component {
    state = {
        src: null,
    };

    componentWillMount() {
        // const src = "http://localhost:8082/sample_project/sample_run";
    }

    render() {
        // const {} = this.state;
        const {children, ...props} = this.props;
        return (
            <div {...props}>{children}</div>
        )
    }
}
