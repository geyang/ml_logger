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
import InlineFile, {ImageView, VideoView} from "../../Charts/FileViews";
import {fromGlobalId, toGlobalId} from "../../lib/relay-helpers";
import {by, firstItem, strOrder} from "../../lib/string-sort";
import ExperimentView from "../../Charts/ExperimentView";

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

const StyledHeader = styled.div`
    padding: 12px 6px;
    overflow: visible;
    display: block;
    box-sizing: border-box;
    margin: 0;
    border: none;
    height: 42px;
    position: relative;
    .root {
      font-weight: normal;
      position: absolute;
      top: 3px;
      left: 6px;
      font-size: 9px;
    }
`;

function HeaderCell({width, children}) {
  if (children === null || typeof children === "undefined" || typeof children === "object")
    return <StyledHeader style={{width: width, color: "#a3a3a3"}}>N/A</StyledHeader>;
  const [root, ...rest] = children.split('.');
  return <StyledHeader title={children} style={{width: width}}>
    <span className="root">{root}</span>
    .{rest.join('.')}
  </StyledHeader>;
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
    {expanded ? <Eye size={24}/> : <EyeOff size={24}/>}
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
                                      //addInlineCharts,
                                      shownInlineCharts,
                                      showInlineCharts, // call with (shownRows: [], shownRows: object, show: bool)
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
  // const [showChart, setShowChart] = useState({});
  const selected = trueDict(selectedRows);
  const [rowExpand, setRowExpand] = useState({});

  function toggleRowExpand(key) {
    setRowExpand({...rowExpand, [key]: !rowExpand[key]})
  }

  const defaultHidden = {};
  if (inlineCharts.length) //note: default show 3 experiments. Only when charts are available.
    exps.slice(0).forEach(({id}) => defaultHidden[id] = true);

  keys = keys.length ? keys : unique(exps.flatMap(exp => exp.parameters.keys));
  keys = minus(keys, hideKeys);


  let df = new DataFrame(exps.map(exp => ({
    id: exp.id,
    metricsPath: exp.metrics ? exp.metrics.path : null,
    expDirectory: fromGlobalId(exp.id).id,
    ...(exp.parameters && exp.parameters.flat || {})
  })));

  //todo: use nested children

  const allKeys = df.listColumns();
  const ids = exps.map(exp => exp.id);

  function toggleSelected(id) {
    let _ = {...selected, [id]: !selected[id]};
    onRowSelect(Object.keys(_).filter(k => _[k]));
  }

  const someSelected = !!Object.keys(selected).length;

  function toggleAllSelected() {
    let _ = someSelected ? {} : trueDict(ids);
    onRowSelect(Object.keys(_).filter(k => _[k]));
  }

  function toggleInlineChart(id) {
    let _ = new Set(shownInlineCharts);
    if (_.has(id)) _.delete(id);
    else _.add(id);
    showInlineCharts(_);
  }

  function toggleAllShowInlineCharts() {
    let _ = shownInlineCharts.size ? [] : ids;
    showInlineCharts(new Set(_));
  }

  let sorted = sortBy.length ? df.sortBy(sortBy) : df;
  // note: id is always aggregated
  const aggKeys = unique(['id', 'metricsPath', 'expDirectory', ...agg, ...match(allKeys, groupBy), ...ignore]);
  const groupKeys = minus(allKeys, aggKeys);

  const grouped = sorted.groupBy(...groupKeys)
      .aggregate(group => group.select(...intersect(aggKeys, allKeys)).toDict());

  df = new DataFrame({
    ...grouped.select(...groupKeys).toDict(),
    ...new DataFrame(grouped.select('aggregation').toDict().aggregation || []).toDict()
  });

  // const expList = df.toCollection();
  const expList = grouped.toCollection().map(function ({aggregation, ..._group}, ind) {

    const children = [...new DataFrame(aggregation).toCollection().map(child => ({
      ..._group, ...child, key: child.id
    }))];

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
        <ShowChart expanded={shownInlineCharts.has(_.key)} onClick={() => toggleInlineChart(_.key)}/>,
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
        <ShowChart expanded={shownInlineCharts.has(_.key)} onClick={() => toggleInlineChart(_.key)}/>,
      ];
      return rowExpand[aggregation.id]
          ? [_, ...children.map(c => ({
            ..._group, ...c,
            key: c.id,
            __className: "child",
            __leftGutter: [
              <SelectRow checked={selected[c.id]} onClick={() => toggleSelected(c.id)}/>,
              <ShowChart expanded={shownInlineCharts.has(c.id)} onClick={() => toggleInlineChart(c.id)}/>
            ]
          }))] : _;
    }
  })
      .sort(by((a, b) => (typeof a === 'string' && typeof b === 'string') ? strOrder(a, b) : 0, "expDirectory"))
      .reverse()
      .flatten();

  const gutterCol = {
    dataIndex: "__leftGutter",
    title: <GutterCell width={120}>
      <SelectRow checked={someSelected} onClick={toggleAllSelected}/>
      <ShowChart expanded={shownInlineCharts.size} onClick={toggleAllShowInlineCharts}/>
    </GutterCell>, //toTitle
    width: 120,
    render: (value, row, index) => <GutterCell width={120}>{value}</GutterCell>
  };
  if (!shownInlineCharts.size)
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
            expandedRowKeys={[...shownInlineCharts]}
            expandedRowRender={(exp, expIndex, indent, expanded) =>
                expanded
                    ? <Grid style={{height: "224px"}}
                            height="auto"
                            rows="100px"
                            columns="small" overflow={true}>
                      {inlineCharts.map(({type, ...chart}, i) => {
                        console.log(type, chart, exp.metricsPath);
                        switch (type) {
                          case "series":
                            //todo: add title
                            return <Box as={LineChart}
                                        key={i}
                                        metricsFiles={
                                          typeof exp.metricsPath === 'string' ? [exp.metricsPath]
                                              : (exp.metricsPath || [])}
                                        color={colorMap(expIndex)}
                                        {...chart}/>;
                          case "file":
                          case "video":
                          case "mov":
                          case "movie":
                          case "img":
                          case "image":
                            return <InlineFile key={i}
                                               type={type}
                                               cwd={exp.expDirectory}
                                               glob={chart.glob}
                                               src={chart.src}
                                               {...chart}/>;
                          default:
                            return null;
                        }
                      })}
                      <ExperimentView id={exp.id}
                                      showHidden={true}
                                      onClick={() => null}/>
                    </Grid>
                    : null
            }
        />
        {/*</ReactDragListView.DragColumn>*/}
      </Box>
  )
}

