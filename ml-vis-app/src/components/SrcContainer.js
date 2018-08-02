import React, {Component} from 'react'
import selector from "../lib/react-luna";

// takes in src, chartKey and a charting component. Outputs the chart.
const cacheKey = 'srcCache';

class _SrcContainer extends Component {
    state = {
        // note: we use a neutral default, to avoid consumers from assuming [] or {}
        data: null,
    };


    static getDerivedStateFromProps(props, state) {
        const {cache, src} = props;
        const {data} = cache[src] || {};
        // if ((!state.data || !state.data.length) && !data) return null;
        if (data === null || data === undefined) return null;
        if (state.data !== data) return {data};
        return null;
    }

    componentDidMount() {
        const {cache, src, fetchCallback} = this.props;
        const {data, $dirty, $fetching} = cache[src] || {};
        //todo: use $dirty
        if (!$fetching && !data && typeof fetchCallback === 'function') fetchCallback(src);
    }

    componentDidUpdate() {
        const {cache, src, fetchCallback} = this.props;
        const {data, $dirty, $fetching} = cache[src] || {};
        //todo: use $dirty
        if (!$fetching && !data && typeof fetchCallback === 'function') fetchCallback(src);
    }


    render() {
        const {children, component: Component, fetchCallback, cache, ...props} = this.props;
        const {data} = this.state;
        if (Component) {
            return <Component data={data} {...props}>{children}</Component>;
        } else if (typeof children === 'function') {
            return children(data);
        }
    }
}

export const SrcContainer = selector(s => ({cache: s[cacheKey]}), _SrcContainer);
