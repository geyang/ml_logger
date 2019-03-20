import React, {Fragment, useState, useRef} from "react";
import styled from "styled-components";
import 'resize-observer-polyfill'
import useComponentSize from '@rehooks/component-size'
import {
  Grid, Box,
  // Table, TableHeader, TableBody, TableRow, TableCell,
  Image, Video,
  CheckBox, RangeInput
} from "grommet";
import ReactDragListView from "react-drag-listview";
import Table from "rc-table";
import './table.css';
import 'react-resizable/css/styles.css';
import {Eye, EyeOff, Plus, MinusSquare, Square, CheckSquare} from 'react-feather';
import DataFrame from "dataframe-js";
import {minus, unique, match, intersect} from "../../lib/sigma-algebra";
import LineChart from "../../Charts/LineChart";
import {colorMap} from "../../Charts/chart-theme";

function trueDict(keys = []) {
  let _ = {};
  keys.forEach(k => _[k] = true);
  return _
}

const StyledCell = styled.div`
    padding: 12px 6px;
    overflow: visible;
    display: block;
    box-sizing: border-box;
    margin: 0;
    border: none;
    height: 42px;
`;

function HeaderCell({width, children}) {
  return (children === null || typeof children === "undefined")
      ? <StyledCell style={{width: width, color: "#a3a3a3"}}>N/A</StyledCell>
      : <StyledCell title={children} style={{width: width}}>{children}</StyledCell>;
}

function TableCell({width, children}) {
  if (children === null || typeof children === "undefined")
    return <StyledCell title="value is `null`" style={{width: width, color: "#a3a3a3"}}>N/A</StyledCell>
  else if (children === true)
    return <StyledCell title={children} style={{width: width}}>True</StyledCell>;
  else if (children === false)
    return <StyledCell title={children} style={{width: width}}>False</StyledCell>;
  return <StyledCell title={children} style={{width: width}}>{children}</StyledCell>;
}


function Multiple(values) {
  return <>
    <strong>{"["}</strong>
    ...
    <strong>{"]"}</strong>
  </>;
}

const StyledGutterCell = styled.div`
    overflow: visible;
    display: inline-block;
    box-sizing: border-box;
    margin: 0;
    border: 0 solid white;
    text-align: right;
`;

function GutterCell({width, ..._props}) {
  return <StyledGutterCell style={{width}} {..._props}/>;
}

function Expand({expanded, ..._props}) {
  return <div style={{
    display: "inline-block",
    padding: "9px 9px 9px 4.5px",
    cursor: "pointer", height: "42px",
    boxSizing: "border-box",
    touchCallout: "none", userSelect: "none"
  }} {..._props}>
    {expanded ? <MinusSquare size={24}/> : <Plus size={24}/>}
  </div>
}

function ShowChart({expanded, ..._props}) {
  return <div style={{
    display: "inline-block",
    padding: "9px 9px 9px 4.5px",
    cursor: "pointer", height: "42px",
    boxSizing: "border-box",
    touchCallout: "none", userSelect: "none"
  }} {..._props}>
    {expanded ? <EyeOff size={24}/> : <Eye size={24}/>}
  </div>
}

function SelectRow({checked, ..._props}) {
  return <div style={{
    display: "inline-block",
    padding: "9px 9px 9px 4.5px",
    cursor: "pointer", height: "42px",
    boxSizing: "border-box",
    touchCallout: "none", userSelect: "none"
  }} {..._props}>{
    checked ? <CheckSquare size={24}/> : <Square size={24}/>
  }</div>
}


export default function ParamsTable({
                                      exps,
                                      keys = [],
                                      hideKeys = [],
                                      sortBy = [],
                                      agg = [], // seed
                                      ignore = [],
                                      groupBy = null, // regEx: Args.*
                                      onKeyChange,
                                      onClick, // not implemented
                                      selectedRows,
                                      onRowSelect, // call with (selections: [], selection: object, select: bool)
                                      inlineCharts,
                                      onColumnDragEnd,
                                      ..._props
                                    }) {

  keys = typeof keys === 'string' ? [keys] : keys;
  sortBy = typeof sortBy === 'string' ? [sortBy] : sortBy;
  agg = typeof agg === 'string' ? [agg] : agg;
  ignore = typeof ignore === 'string' ? [ignore] : ignore;

  // const dragProps = {onDragEnd: onColumnDragEnd, nodeSelector: "th div.drag-handle"};

  let containerRef = useRef(null);
  let {width, height} = useComponentSize(containerRef);


  // const [selected, setSelected] = useState(trueDict(selectedRows));
  const selected = trueDict(selectedRows);
  const [rowExpand, setRowExpand] = useState({});
  const [showChart, setShowChart] = useState({});

  function toggleRowExpand(key) {
    setRowExpand({...rowExpand, [key]: !rowExpand[key]})
  }

  function toggleShowChart(key) {
    setShowChart({...showChart, [key]: !showChart[key]})
  }

  const defaultHidden = {};
  if (inlineCharts.length) //note: default show 3 experiments. Only when charts are available.
    exps.slice(0).forEach(({id}) => defaultHidden[id] = true);
  const [hidden, setHidden] = useState(defaultHidden);
  const [bySelection, setBySelection] = useState(false);

  keys = keys.length ? keys : unique(exps.flatMap(exp => exp.parameters.keys));
  keys = minus(keys, hideKeys);


  let df = new DataFrame(exps.map(exp => ({
    id: exp.id,
    metricsPath: exp.metrics ? exp.metrics.path : null,
    ...(exp.parameters && exp.parameters.flat || {})
  })));

  //todo: use nested children

  const allKeys = df.listColumns();
  const ids = exps.map(exp => exp.id);

  const someShown = Object.keys(hidden).length !== exps.length;
  const toggleHidden = (expanded, {id}) => setHidden({...hidden, [id]: !expanded});
  const toggleAllHidden = () => setHidden(someShown ? trueDict(ids) : {});

  const someSelected = !!Object.keys(selected).length;

  function toggleSelected(id) {
    let newSelected = {...selected, [id]: !selected[id]};
    console.log(newSelected);
    // setSelected(newSelected);
    if (typeof onRowSelect === 'function')
      onRowSelect(
          Object.keys(newSelected).filter(k => newSelected[k]),
          id,
          !selected[id]
      );
  }

  function toggleAllSelected() {
    let newSelected = someSelected ? {} : trueDict(ids);
    // setSelected(newSelected);
    if (typeof onRowSelect === 'function')
      onRowSelect(
          Object.keys(newSelected).filter(k => newSelected[k]),
          ids,
          !someSelected
      );
  }

  let sorted = sortBy.length ? df.sortBy(sortBy) : df;
  // note: id is always aggregated
  const aggKeys = unique(['id', 'metricsPath', ...agg, ...match(allKeys, groupBy), ...ignore]);
  const groupKeys = minus(allKeys, aggKeys);

  const grouped = sorted.groupBy(...groupKeys)
      .aggregate(group => group.select(...intersect(aggKeys, allKeys)).toDict());

  df = new DataFrame({
    ...grouped.select(...groupKeys).toDict(),
    ...new DataFrame(grouped.select('aggregation').toDict().aggregation || []).toDict()
  });

  // const expList = df.toCollection();
  const expList = grouped.toCollection().map(function ({aggregation, ..._group}, ind) {

    const children = [...new DataFrame(aggregation).toCollection()
        .map(child => ({..._group, ...child, key: child.id}))];

    let aggShunt = {};
    Object.keys(aggregation).forEach((k) => aggShunt[k] = <Multiple/>);

    if (children.length === 1) {
      let _ = {
        ..._group,
        ...children[0],
        key: children[0].id,
        __className: "single"
      };
      _.__leftGutter = [
        <SelectRow checked={selected[_.key]} onClick={() => toggleSelected(_.key)}/>,
        <ShowChart expanded={showChart[_.key]} onClick={() => toggleShowChart(_.key)}/>
      ];
      return _;
    } else {
      let _ = {
        ..._group,
        // ...aggShunt,
        ...aggregation,
        key: aggregation.id.join(','),
        __className: "group",
      };
      _.__leftGutter = [
        <Expand expanded={rowExpand[_.key]} onClick={() => toggleRowExpand(_.key)}/>,
        <SelectRow checked={selected[_.key]} onClick={() => toggleSelected(_.key)}/>,
        <ShowChart expanded={showChart[_.key]} onClick={() => toggleShowChart(_.key)}/>,
      ];
      return rowExpand[aggregation.id]
          ? [_, ...children.map(c => ({
            ..._group, ...c,
            key: c.id,
            __className: "child",
            __leftGutter: [
              <SelectRow checked={selected[c.id]} onClick={() => toggleSelected(c.id)}/>,
              <ShowChart expanded={showChart[c.id]} onClick={() => toggleShowChart(c.id)}/>
            ]
          }))] : _;
    }
  }).flatten();

  const expandedKeys = Object.keys(showChart).filter(k => showChart[k]);

  const gutterCol = {
    dataIndex: "__leftGutter",
    title: <GutterCell width={120}/>, //toTitle
    width: 120,
    render: (value, row, index) => <GutterCell width={120}>{value}</GutterCell>
  };
  if (!expandedKeys.length)
    gutterCol.fixed = "left";
  const columns = [
    gutterCol,
    ...keys.map((k, ind) => ({
      key: k,
      title: <HeaderCell width={(ind === keys.length - 1) ? 2000 : 50}>{k}</HeaderCell>, //toTitle
      dataIndex: k,
      width: (ind === keys.length - 1) ? 500 : 50,
      textWrap: 'ellipsis',
      // fixed: (ind === 0) ? "left" : null
      render: (value, row, index) =>
          <TableCell width={(ind === keys.length - 1) ? 2000 : 50}>{value}</TableCell>
    }))];

  const totalWidth = columns.map(k => k.width).reduce((a, b) => a + b, 0);

  const keyWidth = {};
  columns.forEach(({key, width}) => keyWidth[key] = width);

  return (
      <Box ref={containerRef} {..._props} flex={true}>
        {/*<ReactDragListView.DragColumn {...dragProps}>*/}
        <Table
            columns={columns}
            className="bordered fixed"
            data={expList}
            // data={expList.map((exp, ind) => ({key: exp.id || ind, ...exp}))}
            rowSelection={() => null}
            size="small"
            bordered
            scroll={{x: totalWidth + 200, y: height - 42}}
            // onExpand={toggleHidden}
            expandRowByClick
            rowClassName={(row) => row.__className || ""}
            expandedRowKeys={expandedKeys}
            expandedRowRender={(exp, expIndex, indent, expanded) =>
                expanded
                    ? <Grid style={{minHeight: "200px"}}
                            height="auto"
                            rows="100px"
                            columns="small" overflow={true}>
                      {inlineCharts.map(({type, ...chart}, i) => {
                        console.log(type, chart, exp.metricsPath);
                        switch (type) {
                          case "series":
                            return <Box as={LineChart}
                                        key={i}
                                        metricsFiles={exp.metricsPath}
                                        color={colorMap(expIndex)}
                                        {...chart}/>;
                          case "img":
                            return <Box key={i}>
                              <Image src={chart.path.replace('$range', chart.range.value)}
                                     style={{maxWidth: 200, maxHeight: 300}}/>
                              {chart.range ?
                                  <RangeInput value={chart.range.value} onChange={() => null}/> : null}
                            </Box>;
                          case "mov":
                            return <Box key={i}>
                              <Video>
                                <source key="video" src={chart.path} type="video/mp4"/>
                                {/*<track key="cc" label="English" kind="subtitles" srcLang="en" src="/assets/small-en.vtt" default/>*/}
                              </Video>
                              {chart.range ?
                                  <RangeInput value={chart.range.value} onChange={() => null}/> : null}
                            </Box>;
                          default:
                            return null;
                        }
                      })}
                    </Grid>
                    : null
            }
        />
        {/*</ReactDragListView.DragColumn>*/}
      </Box>
  )
}

