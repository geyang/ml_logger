import React, {useState, useRef, useEffect, useMemo} from "react";
import {QueryRenderer, createFragmentContainer, createPaginationContainer, createRefetchContainer} from "react-relay";
import graphql from "babel-plugin-relay/macro";
import {by, strOrder} from "../../lib/string-sort";
import styled from "styled-components";
import {modernEnvironment} from "../../data";
import {toGlobalId} from "../../lib/relay-helpers";
import {Col, ColContainer, RowContainer} from "../../components/layouts";
import {VariableSizeGrid as Grid} from 'react-window';

const StyledCell = styled.div`
  cursor: pointer;
  background: ${p => p.odd ? "#f6f6f6" : "white"}
  line-height: 30px;
  &.hover {
    background: ${p => p.odd ? "rgba(27,124,195,0.26)" : "rgba(37,170,255,0.13)"}
  }
`;

function isOdd(i) {
  return i % 2;
}

function ExperimentList({
                          width, height,
                          selected, onSelect,
                          breadCrumbs, directory, loadMore, ..._props
                        }) {
  const {name, directories, experiments} = directory || {};
  const [sorted, setExperiments] = useState([]);

  useEffect(() => {
    setExperiments((experiments && experiments.edges || [])
        .filter(_ => _ !== null)
        .map(({node}) => node)
        .filter(_ => _ !== null)
        .sort(by(strOrder, "path"))
        .reverse());
  }, [experiments]);

  const [hovered, setHoveredRowIndex] = useState(null);
  const itemData = useMemo(() => ({hovered, setHoveredRowIndex}), [hovered]);

  function Cell({columnIndex, rowIndex, data, ..._props}) {
    const {hovered, setHoveredRowIndex} = data;
    let node = sorted[rowIndex];
    if (!node)
      return <StyledCell onClick={loadMore} {..._props}>Load More..</StyledCell>;
    switch (columnIndex) {
      case(0):
        return <StyledCell odd={isOdd(rowIndex)}
                           onMouseDown={(e) => onSelect(e, node)}
                           onMouseEnter={() => setHoveredRowIndex(rowIndex)}
                           className={hovered === rowIndex ? "hover" : null}
                           {..._props}></StyledCell>;
      case(1):
        return <StyledCell odd={isOdd(rowIndex)}
                           onMouseDown={(e) => onSelect(e, node)}
                           onMouseEnter={() => setHoveredRowIndex(rowIndex)}
                           className={hovered === rowIndex ? "hover" : null}
                           {..._props}>{rowIndex + 1}</StyledCell>;
      case(2):
        return <StyledCell odd={isOdd(rowIndex)}
                           onMouseDown={(e) => onSelect(e, node)}
                           onMouseEnter={() => setHoveredRowIndex(rowIndex)}
                           className={hovered === rowIndex ? "hover" : null}
                           {..._props}>{node.name}</StyledCell>;
      case(3):
        return <StyledCell odd={isOdd(rowIndex)}
                           onMouseDown={(e) => onSelect(e, node)}
                           onMouseEnter={() => setHoveredRowIndex(rowIndex)}
                           className={hovered === rowIndex ? "hover" : null}
                           {..._props}>{node.path}</StyledCell>;
      default:
        return <StyledCell odd={isOdd(rowIndex)}
                           onMouseDown={(e) => onSelect(e, node)}
                           onMouseEnter={() => setHoveredRowIndex(rowIndex)}
                           className={hovered === rowIndex ? "hover" : null}
                           {..._props}>...</StyledCell>;

    }
  }

  const el = useRef(null);
  const [measure, setHeight] = useState({width: 200, height: 200});
  useEffect(() => {
    setHeight({height: el.current.clientHeight - 5, width: el.current.clientWidth - 5});
  }, [sorted]);


  const colWidths = [30, 30, 150, 2000];

  return (
      <ColContainer ref={el}
                    fill={true}
                    shrink={true}
                    onMouseLeave={() => setHoveredRowIndex(null)}
                    style={{width, height,}} {..._props}>
        <Grid width={measure.width}
              height={measure.height}
            // height={(sorted.length + 1) * 30}
              columnCount={colWidths.length}
              rowCount={sorted.length + 1}
              columnWidth={index => colWidths[index]}
              rowHeight={() => 30}
              itemData={itemData}
        >{Cell}</Grid>
      </ColContainer>);
}

export default function ({path, ..._props}) {
  let dirID = toGlobalId("Directory", path);
  //todo: move all of these to the reFetch container inside the directory list view.
  //  so that we don't refresh the component on "loadMore"
  const [limit, setLimit] = useState(50);

  function loadMore() {
    setLimit(limit + 50)
  }

  return <QueryRenderer
      environment={modernEnvironment}
      cacheConfig={{force: true}}
      variables={{dirID, first: limit}}
      query={
        graphql`
        query ExperimentListQuery ($dirID:ID!, $first:Int) {
            directory: node(id: $dirID){
                ...on Directory {
                    name
                    experiments (first:$first) {
                        pageInfo { endCursor hasNextPage }
                        edges {
                            cursor
                            node {
                                id
                                name
                                path
                                metrics { value }
                            }
                        }

                    }
                }
            }}
        `}
      render={
        ({error, props, retry}) => <ExperimentList loadMore={loadMore} {...props} {..._props}/>
      }/>;
}
