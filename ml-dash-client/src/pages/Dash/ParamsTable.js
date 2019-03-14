import React, {Fragment, useState, useRef} from "react";
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
import {Eye, EyeOff} from 'react-feather';
import DataFrame from "dataframe-js";
import {minus, unique, match, intersect} from "../../lib/sigma-algebra";
import LineChart from "../../Charts/LineChart";
import {colorMap} from "../../Charts/chart-theme";
import {toTitle} from "../../lib/string-sort";

function trueDict(keys = []) {
  let _ = {};
  keys.forEach(k => _[k] = true);
  return _
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
                                      onSelectRow,  //not implemented
                                      inlineCharts,
                                      onColumnDragEnd,
                                      ..._props
                                    }) {
  console.log(keys);

  keys = typeof keys === 'string' ? [keys] : keys;
  sortBy = typeof sortBy === 'string' ? [sortBy] : sortBy;
  agg = typeof agg === 'string' ? [agg] : agg;
  ignore = typeof ignore === 'string' ? [ignore] : ignore;

  const dragProps = {onDragEnd: onColumnDragEnd, nodeSelector: "th"};

  let containerRef = useRef(null);
  const {width, height} = useComponentSize(containerRef);

  const [selected, setSelected] = useState({});
  const defaultHidden = {};
  if (inlineCharts.length) //note: default show 3 experiments. Only when charts are available.
    exps.slice(3).map(({id}) => defaultHidden[id] = true);
  const [hidden, setHidden] = useState(defaultHidden);
  const [bySelection, setBySelection] = useState(false);

  keys = keys.length ? keys : unique(exps.flatMap(exp => exp.parameters.keys));
  keys = minus(keys, hideKeys);

  console.log(keys);
  console.log(hidden);

  let df = new DataFrame(exps.map(exp => ({
    id: exp.id,
    metricsPath: exp.metrics ? exp.metrics.path : null,
    ...(exp.parameters && exp.parameters.flat || {})
  })));

  const allKeys = df.listColumns();
  const ids = exps.map(exp => exp.id);

  const someShown = Object.keys(hidden).length !== exps.length;
  const toggleHidden = (expanded, {id}) => setHidden({...hidden, [id]: !expanded});
  const toggleAllHidden = () => setHidden(someShown ? trueDict(ids) : {});

  const someSelected = !!Object.keys(selected).length;
  const toggleSelected = id => setSelected({...selected, [id]: !selected[id]});
  const toggleAllSelected = () => setSelected(someSelected ? {} : trueDict(ids));

  let sorted = sortBy.length ? df.sortBy(sortBy) : df;
  const aggKeys = unique(// note: id is always aggregated
      ['id', 'metricsPath', ...agg, ...match(allKeys, groupBy), ...ignore]);
  const groupKeys = minus(allKeys, aggKeys);

  console.log(groupKeys);

  const grouped = sorted.groupBy(...groupKeys)
      .aggregate(group => group.select(...intersect(aggKeys, allKeys)).toDict());

  df = new DataFrame({
    ...grouped.select(...groupKeys).toDict(),
    ...new DataFrame(grouped.select('aggregation').toDict().aggregation || []).toDict()
  });

  const expList = df.toCollection();
  // console.log(expList);

  const expandedKeys = expList.map(({id}) => !hidden[id] ? id : null).filter(id => id !== null);
  // console.log(expandedKeys);

  const columns = keys.map((k, ind) => ({
    key: k,
    title: <div style={{
      width: (ind === keys.length - 1) ? 500 : 50,
      padding: "12px 6px",
      overflow: "hidden",
      display: "inline-block"
    }}>{toTitle(k)}</div>,
    dataIndex: k,
    width: (ind === keys.length - 1) ? 500 : 50,
    textWrap: 'ellipsis',
    // fixed: (ind === 0) ? "left" : null
    render: (value, row, index) =>
        <div style={{
          width: (ind === keys.length - 1) ? 500 : 50,
          padding: "12px 6px",
          overflow: "hidden",
          display: "inline-block"
        }}>{(value === null) ? "None" : (typeof value === 'undefined') ? "N/A" : value}</div>
  }));
  const totalWidth = columns.map(k => k.width).reduce((a, b) => a + b, 0);

  const keyWidth = {};
  columns.forEach(({key, width}) => keyWidth[key] = width);

  // const components = {
  //   // table: MyTable,
  //   header: {
  //     //   wrapper: HeaderWrapper,
  //     //   row: HeaderRow,
  //     cell: ({children, ..._props}) => <td
  //         style={{width: 150, overflow: "hidden", display: "inline-block"}} {..._props}>{children}</td>
  //   },
  //   body: {
  //     // wrapper: BodyWrapper,
  //     // row: BodyRow,
  //     cell: ({children, ..._props}) => <td
  //         style={{width: 150, overflow: "hidden", display: "inline-block"}} {..._props}>{children}</td>
  //   },
  // };

  return (
      <Box ref={containerRef} {..._props} flex={true}>
        <ReactDragListView.DragColumn {...dragProps}>
          <Table
              // components={{
              //   header: {
              //     cell: (value)=> <div style={{}}>{value}</div>,
              //   }
              // }}
              columns={columns}
              className="bordered fixed"
              data={expList.map((exp, ind) => ({key: exp.id || ind, ...exp}))}
              rowSelection={() => null}
              size="small"
              bordered
              scroll={{x: totalWidth, y: height - 55}}
              // expandIconAsCell
              onExpand={toggleHidden}
              expandRowByClick
              expandedRowKeys={expandedKeys}
              // onExpandedRowsChange={() => null}
              expandedRowRender={(exp, expIndex, indent, expanded) =>
                  expanded
                      ? <Grid style={{minHeight: "200px"}} colSpan="100%" height="auto" rows="100px"
                              columns="small" overflow={true}>
                        {inlineCharts.map((chart, i) => {
                          switch (chart.type) {
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
        </ReactDragListView.DragColumn>
      </Box>
  )
}

// function Test() {
//   return <Table fill="full" flex="auto" scrollable={true}>
//     <TableHeader>
//       <TableRow>
//         <Box as={TableCell} justify="left" pad='small' height="36px" direction='row' align="start"
//              fill='horizontal' gap='xsmall' height={56}>
//           <CheckBox alt="Toggle Select All" checked={someSelected} onChange={toggleAllSelected}/>
//           {someShown
//               ? <Box as={EyeOff} onClick={toggleAllHidden} style={{cursor: "pointer"}}/>
//               : <Box as={Eye} onClick={toggleAllHidden} style={{cursor: "pointer"}}/>
//           }</Box>
//         {keys.map((key, i) =>
//             <TableCell scope="col" key={i}>
//               <strong>{toTitle(key)}</strong>
//             </TableCell>
//         )}</TableRow>
//     </TableHeader>
//     <TableBody display="block" overflowY="auto">
//       {expList.map((exp, expIndex) =>
//           <Fragment key={exp.id.toString()}>
//             <TableRow pad="small" direction="exp" height="36px" style={{color: "black", background: "white"}}>
//               <Box as={TableCell} justify="left" pad='small' height="36px" direction='row' align="start"
//                    fill='horizontal' gap='xsmall' height={56}>
//                 <CheckBox checked={selected[exp.id]} onChange={() => toggleSelected(exp.id)}/>
//                 {hidden[exp.id]
//                     ? <Box as={EyeOff} onClick={() => toggleHidden(exp.id)} style={{cursor: "pointer"}}/>
//                     : <Box as={Eye} onClick={() => toggleHidden(exp.id)} style={{cursor: "pointer"}}/>}
//               </Box>
//               {keys.map((key, i) =>
//                   <TableCell key={i} scope="exp">{
//                     exp[key] && exp[key].toString()
//                   }</TableCell>)} </TableRow>
//             {inlineCharts.length && !hidden[exp.id] ?
//                 <TableRow style={{background: "#f8f8f8"}}>
//                   <Grid as={TableCell} colSpan="100%" height="auto" rows="100px" columns="small"
//                         style={{minHeight: 200}}
//                         overflow={true}>
//                     {inlineCharts.map((chart, i) => {
//                       switch (chart.type) {
//                         case "line":
//                           return <Box as={LineChart}
//                                       key={i}
//                                       metricsFiles={exp.metricsPath}
//                                       color={colorMap(expIndex)}
//                                       {...chart}/>;
//                         case "img":
//                           return <Box key={i}>
//                             <Image src={chart.path.replace('$range', chart.range.value)}
//                                    style={{maxWidth: 200, maxHeight: 300}}/>
//                             {chart.range ?
//                                 <RangeInput value={chart.range.value} onChange={() => null}/> : null}
//                           </Box>;
//                         case "mov":
//                           return <Box key={i}>
//                             <Video>
//                               <source key="video" src={chart.path} type="video/mp4"/>
//                               {/*<track key="cc" label="English" kind="subtitles" srcLang="en" src="/assets/small-en.vtt" default/>*/}
//                             </Video>
//                             {chart.range ?
//                                 <RangeInput value={chart.range.value} onChange={() => null}/> : null}
//                           </Box>;
//                         default:
//                           return null;
//                       }
//                     })}
//                   </Grid>
//                 </TableRow> : null}
//           </Fragment>
//       )}
//     </TableBody>
//   </Table>
//
// }
