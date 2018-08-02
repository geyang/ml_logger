import React, {Component} from 'react';
import {Flex} from 'layout-components';
import selector from "../lib/react-luna";

class ParameterBar extends Component {
    state = {};

    render() {
        const {parameters, paramKeys} = this.props;
        return <Flex row>
            {records.map()}
        </Flex>
    }
}
class _ParameterCell extends Component {
    state = {};

    static getDerivedStateFromProps(props, state) {
        return null;
    }

    render() {
        const {parameterKey,...props} = this.props;
        const [key, ...rest] = parameterKey.split(':');
        return <div {...props} >{key}:</div>
    }
}

export const ChartKeyTagInput = selector(({chartKeys}) => ({chartKeys}), _ParameterCell);


