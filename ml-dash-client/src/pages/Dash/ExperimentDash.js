import React, {Fragment} from "react";
import {commitMutation, createFragmentContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import {Grid, Box, Tabs, Tab, Table, TableHeader, TableBody, TableRow, TableCell, Markdown, CheckBox} from "grommet";
import MonacoEditor from "react-monaco-editor";
import {debounce} from "throttle-debounce";
import {toGlobalId} from "../../lib/relay-helpers";

let tempID = 0;

function updateText(environment, fileId, text) {
  return commitMutation(environment, {
    mutation: graphql`
        mutation ExperimentDashMutation($input: MutateTextFileInput!) {
            updateText (input: $input) {
                file { id name path relPath text yaml}
            }
        }
    `,
    variables: {
      input: {id: fileId, text, clientMutationId: tempID++},
    }
  });
}

class ExperimentDash extends React.Component {
  updateDashConfig = debounce(1000, (id, text) => {
    if (!id)
      id = toGlobalId("File", this.props.directory.path + "/default.dashcfg");
    updateText(this.props.relay.environment, id, text);
  });

  updateText = debounce(1000, (id, text) => {
    if (!id)
      id = toGlobalId("File", this.props.directory.path + "/README.md");
    updateText(this.props.relay.environment, id, text);
  });

  render() {
    const {directory, relay, openExperimentDetails, ...props} = this.props;
    const {files, fullExperiments, readme, dashConfigs} = directory;

    // note: place holder
    const selectedExperiments = fullExperiments;

    console.log(directory);

    let dashConfig = dashConfigs.edges.length ? dashConfigs.edges[0].node : {text: ""};

    const allParamKeys = new Set(
        fullExperiments.edges.map(({node}) => node.parameters.keys).flat());
    let _ = dashConfig.yaml && dashConfig.yaml.parameters || [...allParamKeys];
    if (typeof _ === 'string') {
      _ = _.split(',').map(s => s.trim())
    }
    const selectedKeys = _.filter(k => allParamKeys.has(k) || k.key || k.metrics);

    const chartConfigs = dashConfig.yaml && dashConfig.yaml.charts;

    return <Grid style={{width: "100%", height: "100vh"}}
                 gap='none'
                 fill={true}
                 rows={['56px', '200px', ['0px', 'auto'], ['0px', 'auto'], ['auto', '1/4']]}
                 columns={['full']}
                 areas={[
                   {name: 'tab-bar', start: [0, 0], end: [0, 0]},
                   {name: 'dash-config', start: [1, 0], end: [1, 0]},
                   {name: 'main', start: [2, 0], end: [2, 0]},
                   {name: 'readme', start: [3, 0], end: [3, 0]},
                   {name: 'markdown-editor', start: [4, 0], end: [4, 0]},
                 ]} {...props}>
      <Tabs area="tab-bar" align="start">
        <Tab title={'all'}/>
        {dashConfigs.edges.map(({node}) => <Tab key={node.name} title={node.name.split('.')[0]}/>)}
        <Tab title={'+'} border={{side: "bottom", color: "none", size: 0}}/>
      </Tabs>
      <Box area='dash-config'>
        <MonacoEditor
            height="200"
            language="yaml"
            theme="vs-github"
            value={dashConfig && dashConfig.text}
            options={{selectOnLineNumbers: true, folding: true}}
            onChange={(value) => this.updateDashConfig(dashConfig && dashConfig.id, value)}
            editorDidMount={() => null}/>
      </Box>
      <Box area="main" gap='none' direction="column" overflow='auto'>
        <Box justify="left" pad='small' height="36px" direction='row' align="start" fill='horizontal' gap='large'
             height={56}>
          <Box as="h2">Experiments</Box>
          <Box as={CheckBox} label="Inline Plots"/>
        </Box>
        <Table fill="full" flex="auto" scrollable={true}>
          <TableHeader>
            <TableRow>
              <TableCell scope="col">
                <CheckBox label="Select All"/>
              </TableCell>
              {selectedKeys.map(key =>
                  <TableCell scope="col" key={key.metrics || key.key || key}>
                    <strong>{
                      (typeof key === 'string' || key.key) ? key.key || key : key.metrics
                    }</strong>
                  </TableCell>
              )}</TableRow>
          </TableHeader>
          <TableBody display="block" overflowY="auto">
            {fullExperiments.edges.map(({node}) =>
                <Fragment key={node.id}>
                  <TableRow pad="small" direction="row"
                            key={node.id}
                            border={{side: "bottom", color: "gray", size: "1px"}} height="36px"
                            onClick={() => this.props.openExperimentDetails(node, chartConfigs)}>
                    <TableCell><CheckBox/></TableCell>
                    {selectedKeys.map(key =>
                        <TableCell key={key.metrics || key.key || key} scope="row">
                          {
                            (typeof key === 'string' || key.key)
                                ? node.parameters.flat[key.key || key]
                                : node.metrics.value[key.metrics] && node.metrics.value[key.metrics].slice(-1)
                          }</TableCell>)}
                  </TableRow>
                </Fragment>
            )}
          </TableBody>
        </Table>
      </Box>
      <Box area="readme" overflow="auto">
        {readme ? <Markdown tag="article" className="markdown-body entry-content">{readme.text}</Markdown> : null}
      </Box>
      <Box area="markdown-editor">
        <MonacoEditor
            language="markdown"
            theme="vs-github"
            value={readme && readme.text}
            options={{selectOnLineNumbers: true, folding: true}}
            onChange={(value) => this.updateText(readme && readme.id, value)}
            editorDidMount={() => null}/>
      </Box>
    </Grid>
  }
}


export default createFragmentContainer(ExperimentDash, {
  directory: graphql`
      fragment ExperimentDash_directory on Directory {
          name
          path
          files ( first:50 ) @connection(key: "ExperimentDash_files"){
              edges {
                  cursor
                  node { id name }
              }
          }
          readme { id name path relPath text }
          dashConfigs (first:10) {
              edges{
                  cursor
                  node {id name text stem relPath yaml}
              }
          }
          fullExperiments: experiments (first:50) @connection(key: "ExperimentDash_fullExperiments") {
              edges { node {
                  id name path
                  parameters { keys flat}
                  metrics {id keys path value(keys: ["__timestamp", "epoch", "sine"])}
              } }
          }
      }
  `
});

