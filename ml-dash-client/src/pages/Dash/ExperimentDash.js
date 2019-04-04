import React, {Fragment, useRef, useState, useEffect} from "react";
import {useToggle, useMount} from "react-use";
import {commitMutation, createFragmentContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import {Box, Markdown, CheckBox, Button} from "grommet";
import MonacoEditor from "react-monaco-editor";
import {debounce} from "throttle-debounce";
import {toGlobalId} from "../../lib/relay-helpers";
import ParamsTable from "./ParamsTable";
import {ContextMenu} from "./TableContextMenu";
import {DataFrame} from "dataframe-js";
import {ParallelCoordinates} from "../../components/ParallelCoordiantes";
import isGlob from "is-glob";
import minimatch from "minimatch";

let tempID = 0;

function updateText(environment, fileId, text) {
  return commitMutation(environment, {
    mutation: graphql`
        mutation ExperimentDashUpdateMutation($input: MutateTextFileInput!) {
            updateText (input: $input) {
                file { id name path relPath text yaml}
            }
        }
    `,
    variables: {
      input: {id: fileId, text, clientMutationId: tempID++},
    },
    configs: []
  });
}

function deleteFile(environment, fileId) {
  return commitMutation(environment, {
    mutation: graphql`
        mutation ExperimentDashDeleteMutation(
        $input: DeleteFileInput!
        ) {
            deleteFile (input: $input) { ok id }
        }
    `,
    variables: {
      input: {id: fileId, clientMutationId: tempID++},
    },
    configs: [{
      type: 'NODE_DELETE',
      deletedIDFieldName: 'id',
    }]
  });
}

function deleteDirectory(environment, fileId) {
  return commitMutation(environment, {
    mutation: graphql`
        mutation ExperimentDashDeleteDirectoryMutation(
        $input: DeleteDirectoryInput!
        ) {
            deleteDirectory (input: $input) { ok id }
        }
    `,
    variables: {
      input: {id: fileId, clientMutationId: tempID++},
    },
    configs: [{
      type: 'NODE_DELETE',
      deletedIDFieldName: 'id',
    }]
  });
}

function ExperimentDash({
                          directory,
                          openExperimentDetails,
                          relay,
                          ..._props
                        }) {

  const tableContainer = useRef(null);
  const [tSize, setTSize] = useState({width: 0, height: 0});

  const tableResize = function () {
    console.log(tableContainer.current);
    window.r = tableContainer.current;
    let _ = {
      width: tableContainer.current.clientWidth,
      height: tableContainer.current.clientHeight - 79
    };
    console.log(_);
    setTSize(_);
  };

  // console.log(tSize);

  // useMount(() => setTimeout(tableResize, 500));

  const [editDash, toggleDashEdit] = useToggle(false);
  const [showReadme, toggleReadme] = useToggle(false);
  const [editReadme, toggleReadmeEdit] = useToggle(false);
  const [showParallelCoord, toggleParallelCoord] = useToggle(false);

  const updateDashConfig = debounce(1000, (id, text) => {
    if (!id)
      id = toGlobalId("File", directory.path + "/default.dashcfg");
    updateText(relay.environment, id, text);
  });

  const updateReadme = debounce(1000, (id, text) => {
    if (!id)
      id = toGlobalId("File", directory.path + "/README.md");
    updateText(relay.environment, id, text);
  });

  const {files, fullExperiments, readme, dashConfigs: dC} = directory;

  let dashConfigs = (dC && dC.edges || [])
      .map(({node}) => node)
      .filter(_ => _ !== null)
      .map(node => ({
        ...node,
        yaml: node.yaml || {}
      }));

  let experiments = (fullExperiments && fullExperiments.edges || [])
      .map(({node}) => node)
      .filter(_ => _ !== null);
  let parameters = experiments.map(exp => exp.parameters.flat);

  function matchKeys(k, patterns) {
    //todo: factor out the glob ones, use two list for matching.
    if (patterns.indexOf(k))
      return true;
    for (let p of patterns) {
      if (isGlob(p) && minimatch(k, p))
        return true
    }
    return false;
  }

  let includeKeys = ["Args.*"];
  let ignoreKeys = [''];
  let domains = Object.entries(new DataFrame(parameters).toDict())
      .filter(([k, v]) => matchKeys(k, includeKeys) && ignoreKeys.indexOf(k) === -1)
      .map(([k, v]) => ({
        name: k,
        values: [...new Set(v)],
      })).map(d => ({
        domain: [0, d.values.length],
        tickFormat: v => d.values[Math.floor(v)],
        ...d
      }));
  let domainMap = Object.fromEntries(
      domains.map(d => [d.name, d.values]));
  let pcData = parameters.map(p => ({
    ...Object.fromEntries(Object.entries(p)
        .map(([k, v]) => {
              console.log(k, domainMap[k]);
              if (typeof domainMap[k] === 'undefined')
                window.domains = domains;
              return [k, domainMap[k] ? domainMap[k].indexOf(v) : -1]
            }
        ))
  }));

  const dashConfig = dashConfigs[0] || {yaml: {}};

  const inlineCharts = (dashConfig.yaml.charts || [])
      .filter(c => c !== null)
      .map(c => (typeof c === 'string') ? {type: "series", yKey: c} : c)
      .filter(c => (!c.prefix && !c.metricsFiles))
      .map(c => ({...c, type: c.type || "series"}));

  const keys = dashConfig.yaml.keys || [];

  function reorderKeys(from, to) {
    if (to >= keys.length) {
      let k = to - keys.length + 1;
      while (k--) {
        keys.push(undefined);
      }
    }
    keys.splice(to, 0, keys.splice(from, 1)[0]);
    return keys; // for testing
  }

  const [selected, setSelected] = useState([]);
  console.log(selected);

  return (
      <Box
          alignContent="stretch" basis='auto' flex={true}
          direction="column" gap='none' fill={true} {..._props}>
        <Box justify="left" pad='small' height="36px" direction='row' align="start" fill='horizontal' gap='medium'
             height={56} flex={false}>
          <Box as="h2">{dashConfig.name}</Box>
          <Button><strong>+</strong></Button>
          <Box as={CheckBox} label="Dash Config" checked={editDash} onChange={() => toggleDashEdit()}/>
          <Box as={CheckBox} label="Hyper-parameters" checked={showParallelCoord}
               onChange={() => toggleParallelCoord()}/>
          <Box as={CheckBox} label="Readme" checked={showReadme} onChange={() => toggleReadme()}/>
          <Box as={CheckBox} label="Edit" checked={editReadme} onChange={() => toggleReadmeEdit()}/>
        </Box>
        {showParallelCoord ?
            <Box area='dash-config' height={200} flex={false}>
              <ParallelCoordinates
                  height={200}
                  width={2000}
                  data={pcData}
                  domains={domains}
              /></Box>
            : null}
        {editDash ?
            <Box area='dash-config' height={200} flex={false}>
              <MonacoEditor
                  height="200"
                  language="yaml"
                  theme="vs-github"
                  value={dashConfig && dashConfig.text}
                  options={{selectOnLineNumbers: true, folding: true}}
                  onChange={(value) => updateDashConfig(dashConfig && dashConfig.id, value)}
                  editorDidMount={() => null}/>
            </Box> : null}
        <ParamsTable
            area="main"
            style={{minHeight: 200}}
            exps={experiments}
            keys={(dashConfig.yaml.keys || []).filter(k => k !== null)}
            hideKeys={dashConfig.yaml.hide || []}
            agg={dashConfig.yaml.aggregate || []}
            ignore={dashConfig.yaml.aggIgnore || []}
            sortBy={false}
            groupBy={false}
            inlineCharts={inlineCharts}
            onColumnDragEnd={reorderKeys}
            selectedRows={selected}
            onRowSelect={(selected) => setSelected(selected)}
        />
        {selected.length
            ? <ContextMenu selected={selected}
                           deleteDirectory={(id) => {
                             deleteDirectory(relay.environment, id);
                             setSelected([]);
                           }}/>
            : null}
        {showReadme ?
            <Box area="readme" overflow="auto" background="white" fill={true}>
              {readme ? <Markdown tag="article" className="markdown-body entry-content">{readme.text}</Markdown> : null}
            </Box> : null}
        {editReadme ?
            <Box area="readme-editor" height={300} fill={true}>
              <MonacoEditor
                  language="markdown"
                  theme="vs-github"
                  value={readme && readme.text}
                  options={{selectOnLineNumbers: true, folding: true}}
                  onChange={(value) => updateReadme(readme && readme.id, value)}
                  editorDidMount={() => null}/>
            </Box> : null}
        {}
      </Box>)
}


export default createFragmentContainer(ExperimentDash, {
  directory: graphql`
      fragment ExperimentDash_directory on Directory {
          name
          path
          files ( first:5 ) @connection(key: "ExperimentDash_files"){
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
                  metrics {id keys path}
              } }
          }
      }
  `
});

