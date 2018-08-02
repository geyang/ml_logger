import React, {Component} from 'react';
import {WithContext as TagInput} from 'react-tag-input';
import selector from "../lib/react-luna";
import {deleteParamKey, insertParamKey, moveParamKey} from "../lib/file-api";

const sugguestion = [{id: ".*", text: "all (.*)"}];

class _ExperimentParameterFilter extends Component {
    state = {
        tags: []
    };

    static getDerivedStateFromProps(props, state) {
        const {parameterKeys} = props;
        return {tags: parameterKeys.map(k => ({id: k, text: k}))}
    }

    render() {
        const {dispatch, parameterKeys, ...props} = this.props;
        return <TagInput tags={this.state.tags}
                         inline={true}
                         sugguestion={sugguestion}
                         handleDelete={(index) => dispatch(deleteParamKey(index))}
                         handleAddition={(tag) => dispatch(insertParamKey(tag.id))}
                         handleDrag={(tag, index, newIndex) => dispatch(moveParamKey(index, newIndex))}
                         {...props}
        />
    }
}

export const ExperimentParameterFilter = selector(
    ({parameterKeys}) => ({parameterKeys}),
    _ExperimentParameterFilter,
    true
);
