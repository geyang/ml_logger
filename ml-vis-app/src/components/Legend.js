import React from 'react';

export default class Legend extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      items: [
        {title: 'Apples', color: '#3a3'},
        {title: 'Bananas', color: '#fc0'},
        {title: 'Blueberries', color: '#337'},
        {title: 'Carrots', color: '#f93'},
        {title: 'Eggplants', color: '#337'},
        {title: 'Limes', color: '#cf3'},
        {title: 'Potatoes', color: '#766'}
      ],
      searchText: ''
    };
    this._clickHandler = this._clickHandler.bind(this);
    this._searchChangeHandler = this._searchChangeHandler.bind(this);
  }

  _clickHandler(item) {
    const {items} = this.state;
    item.disabled = !item.disabled;
    this.setState({items});
  }

  _searchChangeHandler(searchText) {
    this.setState({searchText});
  }

  render() {
    const {items, searchText} = this.state;
    return (
      <SearchableDiscreteColorLegend
        height={200}
        width={300}
        onSearchChange={this._searchChangeHandler}
        searchText={searchText}
        onItemClick={this._clickHandler}
        items={items}
      />
    );
  }
}
