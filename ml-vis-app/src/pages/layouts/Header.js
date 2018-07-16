import React, {Component} from "react";
import {Link} from "react-router-dom"


export default class NavBar extends Component {
    render() {
        return <div>
            <Link to={'/experiments'}>/experiments</Link>
            <Link to={'/chart'}>/chart</Link>
            <Link to={'/'}>home page</Link>
        </div>;
    };
}


