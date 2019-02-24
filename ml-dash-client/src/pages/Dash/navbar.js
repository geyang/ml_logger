import React from 'react';
import graphql from 'babel-plugin-relay/macro';

class Navbar extends React.Component {
  render() {
    return <div>Navbar</div>
  }
}

export default createPaginationContainer(
    Navbar,
       graphql`
        fragment Experiment_
          directories (first:10) {
              edges {
                  node {
                      id name
                      directories (first:10) {
                          edges {
                              node {
                                  id name
                              }
                          }
                      }
                  }
              }
          }
      `,
)
