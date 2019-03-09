import React, {Fragment, useState} from "react";
import {
  Grid, Box, Table, TableHeader, TableBody, TableRow, TableCell, Image, Video,
  CheckBox, RangeInput
} from "grommet";
import {Eye, EyeOff} from 'react-feather';
import DataFrame from "dataframe-js";
import {minus, unique, match, intersect} from "../../lib/sigma-algebra";
import LineChart from "../../Charts/LineChart";
import {colorMap} from "../../Charts/chart-theme";

function trueDict(keys = []) {
  let _ = {};
  keys.forEach(k => _[k] = true);
  return _
}

export function ParamsTable({
                              exps,
                              keys = [],
                              sortBy = [],
                              agg = [], // seed
                              ignore = [],
                              groupBy = null, // regEx: Args.*
                              onClick, // not implemented
                              onSelectRow,  //not implemented
                              inlineCharts
                            }) {

  keys = typeof keys === 'string' ? [keys] : keys;
  sortBy = typeof sortBy === 'string' ? [sortBy] : sortBy;
  agg = typeof agg === 'string' ? [agg] : agg;
  ignore = typeof ignore === 'string' ? [ignore] : ignore;

  const [selected, setSelected] = useState({});
  const defaultHidden = {};
  if (inlineCharts.length) //note: default show 3 experiments. Only when charts are available.
    exps.slice(3).map(({id}) => defaultHidden[id] = true);
  const [hidden, setHidden] = useState(defaultHidden);
  const [bySelection, setBySelection] = useState(false);

  keys = keys.length ? keys : unique(exps.flatMap(exp => exp.parameters.keys));

  let df = new DataFrame(exps.map(exp => ({
    id: exp.id,
    metricsPath: exp.metrics.path,
    ...exp.parameters.flat
  })));

  const allKeys = df.listColumns();
  const ids = exps.map(exp => exp.id);

  const allShown = Object.keys(hidden).length === 0;
  const toggleHidden = (id) => setHidden({...hidden, [id]: !hidden[id]});
  const toggleAllHidden = () => setHidden(allShown ? trueDict(ids) : {});

  const someSelected = !!Object.keys(selected).length;
  const toggleSelected = (id) => setSelected({...selected, [id]: !selected[id]});
  const toggleAllSelected = () => setSelected(someSelected ? {} : trueDict(ids));

  let sorted = sortBy.length ? df.sortBy(sortBy) : df;
  const aggKeys = unique(// note: id is always aggregated
      ['id', 'metricsPath', ...agg, ...match(allKeys, groupBy), ...ignore]);
  const groupKeys = minus(allKeys, aggKeys);

  const grouped = sorted.groupBy(...groupKeys)
      .aggregate(group => group.select(...intersect(aggKeys, allKeys)).toDict());

  df = new DataFrame({
    ...grouped.select(...groupKeys).toDict(),
    ...new DataFrame(grouped.select('aggregation').toDict().aggregation).toDict()
  });

  const expList = df.toCollection();
  console.log(expList);

  return <Table fill="full" flex="auto" scrollable={true}>
    <TableHeader>
      <TableRow>
        <Box as={TableCell} justify="left" pad='small' height="36px" direction='row' align="start"
             fill='horizontal' gap='xsmall' height={56}>
          <CheckBox alt="Toggle Select All" checked={someSelected} onChange={toggleAllSelected}/>
          {allShown
              ? <Box as={Eye} onClick={toggleAllHidden} style={{cursor: "pointer"}}/>
              : <Box as={EyeOff} onClick={toggleAllHidden} style={{cursor: "pointer"}}/>
          }</Box>
        {keys.map((key, i) =>
            <TableCell scope="col" key={i}>
              <strong>{key}</strong>
            </TableCell>
        )}</TableRow>
    </TableHeader>
    <TableBody display="block" overflowY="auto">
      {expList.map((exp, expIndex) =>
          <Fragment key={exp.id.toString()}>
            <TableRow pad="small" direction="exp" height="36px" style={{color: "black", background: "white"}}>
              <Box as={TableCell} justify="left" pad='small' height="36px" direction='row' align="start"
                   fill='horizontal' gap='xsmall' height={56}>
                <CheckBox checked={selected[exp.id]} onChange={() => toggleSelected(exp.id)}/>
                {hidden[exp.id]
                    ? <Box as={EyeOff} onClick={() => toggleHidden(exp.id)} style={{cursor: "pointer"}}/>
                    : <Box as={Eye} onClick={() => toggleHidden(exp.id)} style={{cursor: "pointer"}}/>}
              </Box>
              {keys.map((key, i) =>
                  <TableCell key={i} scope="exp">{
                    exp[key] && exp[key].toString()
                  }</TableCell>)} </TableRow>
            {inlineCharts.length && !hidden[exp.id] ?
                <TableRow style={{background: "#f8f8f8"}}>
                  <Grid as={TableCell} colSpan="100%" height="auto" rows="100px" columns="small"
                        style={{minHeight: 200}}
                        overflow={true}>
                    {inlineCharts.map((chart, i) => {
                      switch (chart.type) {
                        case "line":
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
                </TableRow> : null}
          </Fragment>
      )}
    </TableBody>
  </Table>
}
