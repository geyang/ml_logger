import React, {Component} from 'react';
import {fileApi} from '../lib/file-api';
import Highlight from "react-highlight";
// import Highlight from '@episodeyang/react-highlight.js/dist/main';


export class Text extends Component {
    state = {};

    componentDidMount() {
        const {src, start, stop} = this.props;
        fileApi.getText(src, null, stop, start).then(content => this.setState({content})).catch(e => console.warn(e));
    }


    render() {
        const {content} = this.state;
        const {format, start, stop, component: Component = 'pre', ...props} = this.props;
        const _text = format ? format(content) : content;
        return <Component {...props}>{_text}</Component>
    }
}


export function TextHighlight (props) {
    return <Text component={Highlight} {...props}/>
}
