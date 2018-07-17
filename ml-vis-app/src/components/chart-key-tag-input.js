import React, {Component} from 'react';
import {WithContext as TagInput} from 'react-tag-input';
import {deleteChartKey, insertChartKey, moveChartKey} from "../lib/file-api";
import selector from "../lib/react-luna";

const sugguestion = [{id: ".*", text: "all (.*)"}];

class _ChartKeyTagInput extends Component {
    state = {
        chartKeys: []
    };

    static getDerivedStateFromProps(props, state) {
        const {chartKeys} = props;
        return {tags: chartKeys.map(k => ({id: k, text: k}))}
    }

    render() {
        const {dispatch, chartKeys, ...props} = this.props;
        return <TagInput tags={this.state.tags}
                         inline={true}
                         sugguestion={sugguestion}
                         handleDelete={(index) => dispatch(deleteChartKey(index))}
                         handleAddition={(tag) => dispatch(insertChartKey(tag.id))}
                         handleDrag={(tag, index, newIndex) => dispatch(moveChartKey(index, newIndex))}
                         {...props}
        />
    }
}

export const ChartKeyTagInput = selector(({chartKeys}) => ({chartKeys}), _ChartKeyTagInput, true);
