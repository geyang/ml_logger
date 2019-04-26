import React, {useState} from 'react';
import graphql from 'babel-plugin-relay/macro';
import {toGlobalId} from "../../lib/relay-helpers";
import {Box, Grid, Markdown} from "grommet";
import Navbar from "./Navbar";
import ExperimentDash from "./ExperimentDash";
import ChartGrid from "./ChartGrid";
import store from "../../local-storage";
import ProfileBlock from "../../components/ProfileBlock";
import {useTitle} from "react-use";


export function DashPrepareVariables({username, project, path}) {
  return {
    id: toGlobalId("Directory", `/${username}/${project}/${path ? path : ""}`)
  }
}

export const DashQuery = graphql`
  query DashQuery($id: ID!) {
    directory (id: $id) {
      id
      name
      ... Navbar_directory
      ... ExperimentDash_directory
    }
  }
`;

export default function Dash({directory, match, ..._props}) {

  const [state, setState] = useState({experiments: [], charts: []});

  const openExperimentDetails = (experiment, charts = []) => {
    console.log(experiment);
    const location = _props.match.location;
    console.log(state.experiments);
    _props.router.replace({...location, query: {...location.query, view: "experiment"}});
    if (!!experiment)
      setState({experiments: [experiment], charts: charts});
  };

  const addExperimentDetails = (experiment, charts = []) => {
    const location = _props.match.location;
    _props.router.replace({...location, query: {...location.query, view: "experiment"}});

    let _ = [...state.experiments, experiment];
    setState({experiments: [...new Set(_)], charts: charts})
  };

  const closeExperimentPane = () => {
    const location = _props.match.location;
    const {view, ...restOfQuery} = location.query;
    _props.router.replace({...location, query: restOfQuery})
  };


  const viewMode = match.location.query.view;
  const isExperimentView = viewMode === "experiment";

  useTitle(directory.name);

  return <Box fill={true}
              direction="row"
              gap="none"
              alignContent="stretch">
    {isExperimentView
        ? null
        : <Navbar width="300px" directory={directory} gridArea="nav" animation={["fadeIn", "slideRight"]}/>}
    <Box gridArea="main" background='white' fill={true} animation="fadeIn">
      <ProfileBlock profile={store.value.profile}/>
      <ExperimentDash directory={directory} openExperimentDetails={openExperimentDetails}/>
    </Box>
    {isExperimentView
        ? <Box gridArea="side-bar" background='white' fill={true} animation="fadeIn">
          <button onClick={closeExperimentPane}>close</button>
          <ChartGrid experiments={state.experiments} charts={state.charts}/>
        </Box>
        : null}
  </Box>;
}
