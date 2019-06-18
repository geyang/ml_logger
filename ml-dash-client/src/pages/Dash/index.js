import React, {useEffect, useRef, useState} from 'react';
import ColumnFinder from "./Navbar";
import {StyledBase, Col, ColContainer, RootRow, Row, RowContainer} from "../../components/layouts";
import store from "../../local-storage";
import ExperimentList from "./ExperimentList";
import styled from "styled-components";
import {FixedHeroBackDrop, GradientBackDrop, StyledHero} from "./header";
import Link from "found/lib/Link";
import {basename, pathJoin, relPath} from "../../lib/path-join";
import {Resizable} from "re-resizable";
import ProfileBlock from "../../components/ProfileBlock";
import {fetchTextFile, fetchYamlFile, TextEditor, TextView} from "../../Charts/FileViews";
import ChartGridView from "./chart-grid-view";
import Ellipsis from "../../components/Form/Ellipsis";

const SquareBadge = styled.div`
  width: 42px;
  height: 42px;
  border-radius: 5px;
  margin: 19px;
  box-sizing: border-box;
`;

const PaddedRowContainer1 = styled(RowContainer)`
  position: sticky;
  top: 0;
  color: #23A6D5;
  padding: 0 30px;
`;
const Button1 = styled(StyledBase)`
  cursor: pointer;
  padding: 0 0.7em;
  line-height: 56px;
  &.selected { border-bottom: 5px solid #23a6d5; }
  &:hover { background: #fafafa; }
`;
const PaddedRowContainer = styled(RowContainer)`
  position: sticky;
  top: 0;
  color: #23A6D5;
  padding: 0 0;
  z-index: 1001;
  background: rgb(247, 250, 251);
`;
const Button = styled(StyledBase)`
  cursor: pointer;
  padding: 0 1.7em;
  line-height: 56px;
  background: transparent;
  &.selected { background: white }
  &.disabled { opacity: 0.3 }
  &:hover :before { 
    content: "";
    box-shadow: 0 0 10px gray; 
  }
`;

const GroupHeader = styled(GradientBackDrop)`
  position: sticky;
  top: 56px;
  z-index: 1000;
  padding: 0 1.7em;
  height: 50px;
  line-height: 50px;
  color: white;
  font-size: 15px;
  font-weight: 400;
  .badge {
    width: auto;
    min-width: 42px;
    max-width: 400px;
    height: 1.5em;
    border-radius: 5px;
    margin-left: 1em;
    padding: 0 0.5em;
    box-sizing: border-box;
    background: #ffffff2b;
    color: white;
    line-height: 1.5em;
    vertical-align: baseline;
    align-self: center;
  }
`;
const GroupBody = styled(StyledBase)`
  padding: 0 0.7em;
  background: #fafafa;
`;

export default function Dash({match, router, ..._props}) {
  const {params: {project, username, path}} = match;
  // let dirID = toGlobalId("Directory", `/${username}/${project}/${path ? path : ""}`);
  let fullPath = `/${username}/${project}/${path ? path : ""}`;

  // breadCrumbs
  const [breadCrumb, set] = useState([fullPath]);
  useEffect(() => {
    set([fullPath]);
  }, [fullPath]); // reset on path change.
  const expand = (dir, depth) => set([...breadCrumb.slice(0, depth + 1), dir]);

  const el = useRef(null);
  useEffect(() => { // scroll to end
    if (el.current) el.current.scrollTo(el.current.scrollWidth, 0);
  }, [breadCrumb[breadCrumb.length - 1]]);

  //main pane
  const [pane, setPane] = useState("path");
  //dash config, move to the editor.
  const [dashConfig, setDashConfig] = useState({keys: [], charts: []});
  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    fetchYamlFile(pathJoin(breadCrumb.slice(-1)[0], ".dash.yml"))
        .then(({node, errors}) => {
          if (running) {
            if (node) setDashConfig(node.yaml || {keys: [], charts: []});
            else setDashConfig({keys: [], charts: []});
          }
        });
    return abort;
  }, [breadCrumb.slice(-1)[0], setDashConfig]);

  //side car
  const [sideCar, setSideCar] = useState("readme");
  const [selected, select] = useState([]);

  const onSelect = (e, experiment) => {
    if (e.ctrlKey || e.metaKey) {
      if (!selected) {
      } else if (selected.indexOf(experiment.path) === -1) {
        select([...selected, experiment.path]);
        setSideCar('all');
      } else {
        select(selected.filter(_ => _ !== experiment.path));
      }
    } else {
      select([experiment.path]);
      if (sideCar !== 'charts') setSideCar('details');
    }
  };

  return <RootRow background="transparent">
    <FixedHeroBackDrop/>
    <ProfileBlock profile={store.value.profile}/>
    <StyledBase as="aside" width="80px" background="white" boxShadow="0 0 5px rgba(0, 0, 0, 0.1)" zIndex={1}>
      <StyledBase><SquareBadge
          as={"img"}
          src="/ml-dash_logo.png" alt="ml-dash logo"
          width={48} height={48}/></StyledBase>
    </StyledBase>
    <ColContainer fill={true} shrink={true} background="transparent">
      {/*header/navbar*/}
      <StyledHero>
        <ColContainer><h1>{project}</h1></ColContainer>
        <RowContainer>
          <Link className="path" to={pathJoin(fullPath, "../")}>../</Link>
          {breadCrumb.slice(1).map((path, ind) =>
              <Link className="path" key={path} to={path}>{basename(path)}</Link>)}
        </RowContainer>
      </StyledHero>
      {/*experiment list container*/}
      <ColContainer fill={true} overflow={false}>
        <PaddedRowContainer1 height="56px"
                             background="white" zIndex={10}
                             boxShadow="0 0 20px rgba(1,1,1,0.1)">
          <Button1 onClick={() => setPane("path")}
                   className={pane === "path" ? "selected" : null}>PATH</Button1>
          <Button1 onClick={() => setPane("chart")}
                   className={pane === "chart" ? "selected" : null}>CHART</Button1>
          <Button1 onClick={() => setPane(null)}>HyperParameters</Button1>
        </PaddedRowContainer1>
        <Resizable enable={{"bottom": true}}
                   defaultSize={{width: "auto", height: 250}}>{(() => {
          switch (pane) {
            case "chart":
              return <TextEditor path={pathJoin(breadCrumb.slice(-1)[0], ".dash.yml")}/>;
            case "path":
            default:
              return <RowContainer height="calc(100% - 10px)" background={"#f5f5f5"} ref={el}>{
                breadCrumb.map((path, depth) =>
                    <ColumnFinder key={path}
                                  width="250px"
                                  minWidth="250px"
                                  height="100%"
                                  fill={depth === (breadCrumb.length - 1)}
                                  path={path}
                                  selected={breadCrumb[depth + 1]}
                                  onClickDir={(dir) => expand(dir, depth)} gridArea="nav"
                                  animation={["fadeIn", "slideRight"]}/>
                )
              }</RowContainer>;
          }
        })()}
        </Resizable>
        <ExperimentList path={breadCrumb.slice(-1)[0]} onSelect={onSelect} selected={selected}/>
      </ColContainer>
    </ColContainer>

    <ColContainer as={Resizable}
                  fill={true} shrink={true}
                  overflow={"visible"}
                  background="transparent"
                  enable={{"left": true}}
                  defaultSize={{width: "50%", height: "100%vh"}}
    ><ColContainer height="auto"
                   background="white"
                   style={{marginLeft: "20px", marginTop: "50px"}}
                   overflow={false}
                   boxShadow="0 0 20px rgba(0, 0, 0, 0.1)">
      {/*detail view, start with chart view*/}
      {/*<Resizable*/}
      {/*    enable={{"bottom": true}}*/}
      {/*    defaultSize={{width: "auto", height: 400}}><pre><TextView*/}
      {/*    path={breadCrumb.slice(-1)[0] + "/README.md"}/></pre></Resizable>*/}
      <ColContainer overflow={false}>
        <PaddedRowContainer height="56px" background="white">
          <Button className={sideCar === "readme" ? "selected" : null}
                  onClick={() => setSideCar('readme')}>README</Button>
          <Button className={sideCar === "all" ? "selected" : null}
                  onClick={() => setSideCar('all')}>ALL</Button>
          <Button
              className={`${sideCar === "details" ? "selected" : null} ${(selected && selected.length) ? null : "disabled"}`}
              onClick={selected && selected.length ? () => setSideCar('details') : () => null}>DETAILS</Button>
          <Button className={sideCar === "charts" ? "selected" : null}
                  onClick={() => setSideCar('charts')}>CHARTS</Button>
        </PaddedRowContainer>
        <div>{
          (() => {

            let firstSelection = selected[0];

            switch (sideCar) {
              case "readme":
                return <Resizable key={"readme-editor"}
                                  enable={{"bottom": true}}
                                  defaultSize={{width: "auto", height: 800}}><TextEditor
                    path={pathJoin(breadCrumb.slice(-1)[0], "README.md")}/></Resizable>;
              case "all":
                return <>{
                  selected.map((expPath, i) =>
                      <ColContainer key={expPath} overflow={false}>
                        <GroupHeader>
                          RUN:<Ellipsis className="badge" title={expPath} text={expPath} padding="1em"/>
                        </GroupHeader>
                        <GroupBody minHeight="250px"><ChartGridView expPath={expPath} chartsConfig={dashConfig.charts}/></GroupBody>
                      </ColContainer>
                  )}</>;
              case "charts":
                return <><Resizable key={"charts-editor"}
                                    enable={{"bottom": true}}
                                    defaultSize={{width: "auto", height: 200}}
                ><TextEditor path={pathJoin(firstSelection, ".charts.yml")}/></Resizable>
                  <ColContainer overflow={false}>
                    <GroupHeader>
                      RUN:<Ellipsis className="badge" title={firstSelection} text={firstSelection} padding="1em"/>
                    </GroupHeader>
                    <GroupBody minHeight="250px">{firstSelection ?
                        <ChartGridView expPath={firstSelection}/> : null}</GroupBody>
                  </ColContainer></>;
              case "details":
              default:
                return <><Resizable key={"details-readme"}
                                    enable={{"bottom": true}}
                                    defaultSize={{width: "auto", height: 200}}
                ><TextEditor path={pathJoin(firstSelection, "README.md")}/></Resizable>
                  <ColContainer overflow={false}>
                    <GroupHeader>
                      RUN:<Ellipsis className="badge" title={firstSelection} text={firstSelection} padding="1em"/>
                    </GroupHeader>
                    <GroupBody minHeight="250px">{firstSelection ?
                        <ChartGridView expPath={firstSelection}/> : null}</GroupBody>
                  </ColContainer></>;
            }
          })()
        }</div>
        {/*<ParameterTable path={path} selections={}/>;*/}
      </ColContainer>
      {/*list group: */}
      {/*<ColContainer overflow={false}>*/}
      {/*  <GroupHeader>FILES</GroupHeader>*/}
      {/*  <GroupBody><ChartGridView path={breadCrumb.slice(-1)[0]}/></GroupBody>*/}
      {/*</ColContainer>*/}
    </ColContainer></ColContainer>
  </RootRow>
}
