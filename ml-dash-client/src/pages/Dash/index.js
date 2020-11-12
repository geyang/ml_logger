import React, {useEffect, useRef, useState} from 'react';
import ColumnFinder from "./Navbar";
import {StyledBase, Col, ColContainer, RootRow, Row, RowContainer} from "../../components/layouts";
import store from "../../local-storage";
import ExperimentList from "./ExperimentList";
import styled from "styled-components";
import {FixedHeroBackDrop, GradientBackDrop, StyledHero} from "./header";
import {Link} from "found";
import {basename, pathJoin, relPath} from "../../lib/path-join";
import {Resizable} from "re-resizable";
import ProfileBlock from "../../components/ProfileBlock";
import {fetchAllCharts, fetchTextFile, fetchYamlFile, TextEditor, TextView} from "../../Charts/FileViews";
import SelectedGridView from "./selected-grid-view";
import {intersect, minus, union} from "../../lib/sigma-algebra";
import ParameterRow from "../../Charts/ParameterRow";
import Ellipsis from "../../components/Ellipsis-2";
import ChartGridView from "./chart-grid-view";

const SquareBadge = styled.div`
  width: 42px;
  height: 42px;
  border-radius: 5px;
  margin: 19px;
  box-sizing: border-box;
`;

const PaddedRowContainer1 = styled(RowContainer)`
  will-change: transform;
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
  will-change: transform;
  position: sticky;
  top: 0;
  color: #23A6D5;
  padding: 0 0;
  z-index: 1001;
  background: #fafafa;
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
  will-change: transform;
  position: sticky;
  top: 56px;
  z-index: 1000;
  padding: 0 1.7em;
  height: 50px;
  line-height: 50px;
  color: white;
  font-size: 15px;
  font-weight: 400;
  overflow-x: hidden;
  white-space: nowrap;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  > .item {
    height: 100%;
    position: relative;
    > . { 
      display: inline-block !important; 
     }
    .root {
      position: absolute;
      left: 0;
      top: 0.5em;
      height: 10px;
      line-height: 10px;
      font-size: 10px;
      color: white
      font-weight: 600;
    }
  }
  .badge.long {
    min-width: 150px;
  }
  .badge:not(.long):not(:hover) {
    max-width: 200px;
  }
  .badge {
    overflow: hidden;
    width: auto;
    display: inline-block;
    text-overflow: ellipsis;
    height: 1.5em;
    border-radius: 5px;
    margin: 0 0.5em 0 0.25em;
    padding: 0 0.5em;
    box-sizing: border-box;
    background: #ffffff2b;
    color: white;
    line-height: 1.5em;
    vertical-align: middle;
    align-self: center;
  }
`;
const StyledColContainer = styled(ColContainer)`
background: transparent;
>:first-child {
  border-top-left-radius:10px;
  border-top-right-radius:10px;
}
>:last-child {
  border-bottom-left-radius:10px;
  border-bottom-right-radius:10px;
}
`;
const GroupBody = styled(StyledBase)`
  padding: 0 0;
  background: white;
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
  // Remove dashConfig support from server and client
  const [dashConfig, setDashConfig] = useState({keys: [], charts: []});
  useEffect(() => {
    let running = true;
    const abort = () => running = false;
    fetchYamlFile(pathJoin(breadCrumb.slice(-1)[0], ".dash.yml"))
        .then(({node, errors}) => {
          if (running)
            setDashConfig({keys: [], charts: [], ...(node && node.yaml || {})})
        });
    return abort;
  }, [breadCrumb.slice(-1)[0], setDashConfig]);


  //side car
  const [sideCar, setSideCar] = useState("readme");

  const [selected, select] = useState([]);


  const onSelect = (e, ...experiments) => {
    if (e.ctrlKey || e.metaKey) {
      e.stopPropagation();
      if (selected.indexOf(experiments[0].path) === -1) {
        select([...selected, experiments[0].path]);
        setSideCar('all');
      } else {
        let new_selected = selected.filter(_ => _ !== experiments[0].path)
        //set the sideCar to default if the selection is empty.
        if (new_selected.length === 0) setSideCar('readme')
        select(new_selected);
      }
    } else if (e.shiftKey) {
      let newPaths = experiments.map(_ => _.path);
      let newSelection = minus(union(selected, newPaths), intersect(selected, newPaths));
      select(newSelection);
      setSideCar('charts');
    } else {
      select([experiments[0].path]);
      setSideCar('all');
    }
  };

  return <RootRow background="transparent">
    <FixedHeroBackDrop/>
    <ProfileBlock profile={store.value.profile}/>
    <StyledBase as="aside" width="80px" background="white" boxShadow="0 0 20px rgba(0, 0, 0, 0.1)" zIndex={20}>
      <StyledBase as="a" href="/favicon.ico"><SquareBadge
          as={"img"}
          title={"ML-Dash | Make Research Fun"}
          src="/ml-dash_logo.png" alt="ML-Dash | Make Research Fun | logo"
          width={48} height={48}/></StyledBase>
    </StyledBase>
    <ColContainer as={Resizable}
                  enable={{"right": true}}
                  defaultSize={{width: "35%", height: "100%vh"}}
                  handleStyles={{right: {zIndex: 1000}}}
                  fill={false} shrink={false}
                  background="transparent">
      {/*header/navbar*/}
      <StyledHero style={{paddingRight: 0}}>
        <ColContainer><h1>{project}</h1></ColContainer>
        <RowContainer>
          <Link className="path" to={pathJoin(fullPath, "../")}>../</Link>
          <div className="path" onClick={() => set(breadCrumb.slice(0, 1))}>{basename(fullPath)}</div>
          {breadCrumb.slice(1).map((path, ind) =>
              <Link className="path" key={path} to={path}>{basename(path)}</Link>)}
        </RowContainer>
      </StyledHero>
      {/*experiment list container*/}
      <ColContainer fill={true}>
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

    <ColContainer fill={true} shrink={true}
                  background="transparent"
                  style={{marginLeft: "-20px"}}
    ><ColContainer height="auto"
                   style={{marginLeft: "20px", marginTop: "50px", zIndex: 100}}
                   boxShadow="0 0 20px rgba(0, 0, 0, 0.3)">
      <StyledColContainer>
        <PaddedRowContainer height="56px" background="white">
          <Button className={sideCar === "readme" ? "selected" : null}
                  onClick={() => setSideCar('readme')}>README</Button>
          <Button className={sideCar === "charts" ? "selected" : null}
                  onClick={() => setSideCar('charts')}>CHARTS</Button>
          {selected.length
              ? <Button className={sideCar === "all" ? "selected" : null}
                        onClick={() => setSideCar('all')}>SELECTED</Button>
              : null}
          <Button className={sideCar === "diff" ? "selected" : null}
                  onClick={() => setSideCar('diff')}>DIFF</Button>
        </PaddedRowContainer>
        {
          (() => {
            let firstSelection = selected[0];

            switch (sideCar) {
              case "readme":
                return <Resizable key={"readme-editor"}
                                  enable={{"bottom": true}}
                                  defaultSize={{width: "auto", height: 800}}><TextEditor
                    path={pathJoin(breadCrumb.slice(-1)[0], "README.md")}/></Resizable>;
              case "charts":
                // 1. look for ".charts" in the current folder
                // 2. add chart view to markdown
                return <StyledColContainer overflow={false}>
                  <GroupHeader>
                    PATH: <Ellipsis className="badge long"
                                    title={firstSelection}>{breadCrumb.slice(-1)[0]}</Ellipsis>
                    {/* start with keys */}
                    <ParameterRow path={firstSelection}/>
                  </GroupHeader>
                  <GroupBody minHeight="250px"><ChartGridView path={breadCrumb.slice(-1)[0]}/></GroupBody>
                </StyledColContainer>;
              case "details":
              case "all":
              default:
                return <>
                  {(selected && selected.length > 1) ?
                      <Resizable key={"details-readme"}
                                 enable={{"bottom": true}}
                                 defaultSize={{width: "auto", height: 200}}>
                        <TextEditor content={selected.join(',\n')} onChange={false}/>
                      </Resizable>
                      : null}
                  {selected.map((expPath, i) =>
                      <StyledColContainer key={expPath} overflow={false}>
                        <GroupHeader>
                          RUN: <Ellipsis className="badge long"
                                         title={expPath}>{expPath}</Ellipsis>
                          {/* start with keys */}
                          <ParameterRow path={expPath} paramKeys={dashConfig.keys}/>
                        </GroupHeader>
                        <GroupBody minHeight="250px"><SelectedGridView expPath={expPath}
                                                                       chartsConfig={dashConfig.charts}
                        /></GroupBody>
                      </StyledColContainer>
                  )}</>;
            }
          })()
        }
        {/*<ParameterTable path={path} selections={}/>;*/}
      </StyledColContainer>
      {/*list group: */}
      {/*<ColContainer overflow={false}>*/}
      {/*  <GroupHeader>FILES</GroupHeader>*/}
      {/*  <GroupBody><ChartGridView path={breadCrumb.slice(-1)[0]}/></GroupBody>*/}
      {/*</ColContainer>*/}
    </ColContainer></ColContainer>
  </RootRow>
}
