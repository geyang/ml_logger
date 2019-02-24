import React from 'react';
import graphql from 'babel-plugin-relay/macro';
import {ParallelCoordinates} from 'react-vis';

export const SearchQuery = graphql`
    query SearchQuery {
        user (username: "episodeyang") {
            username
            name
            projects(first: 10) {
                edges {
                    node {
                        id
                        name
                        experiments(first:10){ edges { node {
                            name
                            parameters {value keys flat raw}
                            metrics {
                                id
                                keys
                                value (keys: ["__timestamp", "sine"])
                            }
                        } } }
                        directories(first:10){
                            edges {
                                node {
                                    name
                                    files(first:10){
                                        edges {
                                            node { name }
                                        }
                                    }
                                    directories(first:10){
                                        edges {
                                            node { name }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
`;

export default class Search extends React.Component {
  render() {
    const {user} = this.props;
    const project = user.projects.edges[0].node;
    console.log(project);

    const params = project.experiments.edges.map(({node: experiment}) => experiment.parameters.flat);
    console.log(params);

    const domainKeys = ['Args.lr', 'Args.weight_decay', 'Args.lr', 'Args.env_id', 'Args.seed'];

    // const SPECIES_COLORS = {
    //   setosa: '#12939A',
    //   virginica: '#79C7E3',
    //   versicolor: '#1A3177'
    // };

    const domains = params.reduce((acc, row) => {
      return acc.map(d => {
        return {
          name: d.name,
          domain: [
            Math.min(d.domain[0], row[d.name]),
            Math.max(d.domain[1], row[d.name])
          ]
        };
      });
    }, domainKeys.map(name => ({name, domain: [Infinity, -Infinity]})));


    return <div>
      <p>some name</p>
      <ParallelCoordinates animation brushing data={params} domains={domains} margin={60} width={800} height={300}/>
    </div>;
  }
}
