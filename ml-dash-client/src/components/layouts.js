import styled from "styled-components";
import styledContainerQuery from 'styled-container-query';

// ${props => (props.dropShadow ? `
//   &:before {
//     content: "";
//     position: absolute;
//     top: 0;
//     bottom: 0;
//     left: 0;
//     right: 0;
//     z-index: -1;
//     box-shadow: ${props.dropShadow}
// }` : "")};
export const StyledBase = styled.div`
    display: flex;
    scroll-behavior: smooth;
    ${props => (props.width ? "width: " + props.width : "")};
    ${props => (props.height ? "height: " + props.height : "")};
    ${props => (props.minHeight ? "min-height: " + props.minHeight : "")};
    ${props => (props.maxHeight ? "max-height: " + props.maxHeight : "")};
    ${props => (props.minWidth ? "min-width: " + props.minWidth : "")};
    ${props => (props.maxWidth ? "max-width: " + props.maxWidth : "")};
    ${props => (props.lineHeight ? "line-height: " + props.lineHeight : "")};
    ${props => (props.background ? "background: " + props.background : "")};
    ${props => (props.boxShadow ? "box-shadow: " + props.boxShadow : "")};
    ${props => (props.zIndex ? "z-index: " + props.zIndex : "")};
    position: ${props => (props.position)};
    flex: ${props => (props.fill ? "1 " : "0 ") + (props.shrink ? "1 " : "0 ") + "auto"}
    ${props => (props.padding ? "padding: " + props.padding : "")};
`;
export const RootContainer = styled(StyledBase)`
    width: 100%;
    height: 100%;
`;
export const RootRow = styled(RootContainer)`
    flex-direction: row;
`;
const RootCol = styled(RootContainer)`
    flex-direction: column; 
`;
export const RowContainer = styled(StyledBase)`
    ${props => props.overflow === false ? "" : "overflow-x: auto;"};
    flex-direction: row;
    align-items: stretch;
`;
export const ColContainer = styled(StyledBase)`
    ${props => props.overflow === false ? "" : "overflow-y: auto;"};
    flex-direction: column;
    align-items: stretch;
`;

export const Grid = styledContainerQuery(StyledBase)`
  //todo: write this as a list first. Add grid support later
  display: grid;
  width: 100%;
  grid-auto-rows: 250px;
  &:container(max-width: 250px) {
    grid-template-columns: 1fr;
  }
  &:container(min-width: 251px and max-width: 500px) {
    grid-template-columns: 1fr 1fr;
  }
  &:container(min-width: 501px and  max-width: 750px) {
    grid-template-columns: 1fr 1fr 1fr;
  }
  &:container(min-width: 751px and max-width: 1000px) {
    grid-template-columns: 1fr 1fr 1fr 1fr;
  }
  &:container(min-width: 1001px and max-width: 1250px) {
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
  }
  &:container(min-width: 1251px) {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
  justify-items: stretch;
  align-items: stretch;
  > {
    grid-area: auto;
  }
`;
