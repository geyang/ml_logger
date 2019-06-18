import styled from 'styled-components';
import {StyledBase} from "../../components/layouts";

export const FixedHeroBackDrop = styled(StyledBase)`
  position: fixed;
  top: 0;
  width: 100%;
  height: 152px;
  z-index: -1;
  
  background: linear-gradient(-45deg, #EE7752, #E73C7E, #23A6D5, #23D5AB);
  background-size: 400% 400%;
  animation: Gradient 600s ease infinite;

  @keyframes Gradient {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
  }
`;

export const GradientBackDrop = styled(StyledBase)`
  :before {
    content: "";
    z-index: -1;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(-45deg, #EE7752, #E73C7E, #23A6D5, #23D5AB);
    background-size: 800% 800%;
    animation: Gradient-2 600s ease infinite;

    @keyframes Gradient-2 {
      0% { background-position: 12.5% 50% }
      50% { background-position: 100% 50% }
      100% { background-position: 12.5% 50% }
    }
  }
`;
export const StyledHero = styled(StyledBase)`
  color: #fff;
  background: transparent;
  flex-direction: column;
  align-items: stretch;
  
  padding: 15px 30px;
  
  h1 {
    margin-top: 50px;
    font-size: 1.9rem;
    font-weight: 300;
  }
  .path {
    width: fit-content;
    margin-right: 0.5em;
    padding: 0 0.7em;
    border-radius: 4px;
    background: white;
    color: #23A6D5;
    line-height: 32px;
    height: 32px;
    text-decoration: none !important;
  }
`;


