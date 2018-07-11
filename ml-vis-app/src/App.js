import React, {Component} from 'react';
import './App.css';
import LineChartConfidence from "./components/LineChartConfidence";
import {Helmet} from 'react-helmet';
import {Flex, FlexItem} from 'layout-components';
import SearchBox from "./components/SearchBox"
import FileList from "./components/FileList"
import PlotContainer from "./components/PlotContainer"

const eventOutputContainer = document.getElementById("event");
const evtSrc = new EventSource("http://localhost:8082/file-events");

evtSrc.onmessage = function (e) {
    console.log(e.data);
    eventOutputContainer.innerHTML = e.data;
};

class App extends Component {
    state = {
        currentDirectory: "http://localhost:8082/files/",
        files: [],
        logFiles: []
    };

    componentWillMount() {
        const {currentDirectory} = this.state;
        const that = this;
        fetch(currentDirectory)
            .then(r => r.json())
            .then(files => that.setState({files}));
        fetch(currentDirectory)
            .then(r => r.json())
            .then(files => that.setState({
                    logFiles: files.filter(({name}) => name.match(/.*data.pkl/))
                }
            ));
    }

    render() {
        const {currentDirectory, files, logFiles} = this.state;
        return (
            <div className="App">
                <Helmet>
                    <link rel="stylesheet" href="https://unpkg.com/react-vis/dist/style.css"/>
                </Helmet>
                <Flex row fill>
                    <FlexItem fixed component={(props) =>
                        <Flex column {...props}>
                            <FlexItem component={SearchBox}/>
                            <FlexItem component={FileList} files={files}/>
                        </Flex>
                    }/>
                    <FlexItem fluid component={PlotContainer}>
                        {logFiles.map(path => <LineChartConfidence src={path}/>)}
                    </FlexItem>
                </Flex>
            </div>
        );
    }
}

export default App;
