import React from "react";
import styled from "styled-components";

const BoundingBox = styled.div`
  .domains {
    display: flex
    flex-direction: row;
    // align on top
    align-items: flex-start; 
  }
  canvas {
    width: 100%;
    height: 100%;
  }
`;

/* todo:
     1. show coordinates
     2. draw lines on canvas
     3. slave coordinates
     */
export function RealCoord() {
  return <div></div>
}

export function LogCoord() {
  return <div></div>
}

const StyledCategoryCoord = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  > div {
    white-space: nowrap;
    overflow: hidden;
  }
`;

export function CategoryCoord({name, values}) {
  return <StyledCategoryCoord>
    <div>{name}</div>
    {values.map(value => <div>{value}</div>)}
  </StyledCategoryCoord>
}

export function ParallelCoordinates({data, domains, width, height}) {
  // draw selected lines on canvas
  // draw all lines on canvas
  return <BoundingBox>
    <div className="domains" style={{maxHeight: height}}>
      {domains.map(d => {
        switch (d.type) {
          case "real":
            return <RealCoord {...d}/>;
          case "log":
            return <LogCoord {...d}/>;
          case "categorical":
          default:
            return <CategoryCoord {...d}/>;
        }
      })}
    </div>
    <canvas className="selected" width={width} height={height}/>
    <canvas className="all-lines" width={width} height={height}/>
  </BoundingBox>
}
