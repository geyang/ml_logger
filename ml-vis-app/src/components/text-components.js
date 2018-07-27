import React, {Component} from 'react';
import {fileApi} from '../lib/file-api';


export class Text extends Component {
    state = {};

    componentDidMount() {
        const {src, start, stop} = this.props;
        fileApi.getText(src, null, stop, start).then(content => this.setState({content})).catch(e => console.warn(e));
    }


    render() {
        const {content, render, start, stop, component: Component = 'pre', ...props} = this.state;
        const _text = render ? render(content) : content;
        return <Component {...props}>{_text}</Component>
    }
}

