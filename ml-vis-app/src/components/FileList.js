import React from 'react'
import {Flex, FlexItem} from 'layout-components';

export default class FileList extends React.Component {
    state = {
        src: null,
    };

    componentWillMount() {
        // const src = "http://localhost:8082/sample_project/sample_run";
    }

    render() {
        // const {} = this.state;
        const {files = [], ...props} = this.props;
        console.log(files);
        return (
            <Flex fill column {...props}>
                {files.map(f => <FlexItem fixed key={f.name}>{f.name}</FlexItem>)}
            </Flex>
        )
    }
}
