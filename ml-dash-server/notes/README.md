# Implementation Plans

1. build schema
2. make single dataview 
3. make file-list view
4. make diff view
5. make layout
6. make chart key view
7. single experiment view?

## ToDos


- [ ] redirect to profile if no user profile exist

1. show nexted children
click on row to expand

right now the biggest problem is that we don't know how to render only the row on the right. 
Can make-do with some kind of DOM away container, but it is not ideal. 

hidden column:
1. be able to select columns
2. be able to add those to hide
3. show hidden columns
5. select hidden
4. allow unhide
- column head: expand hidden (not a good idea b/c )

allow resizing columns:
1. select column
2. resize
or
1. mouse over
allow reordering of columns:
1. move the header on top

group rows:
1. select row 1
2. select row 2
3. panel opens on the right, show keys that are different
   ```yaml 
   columns: key, exp1, exp2
   ```

select multiple rows:
1. select row 1
2. select row 2
3. panel opens on the right showing different keys
4. select row 3
5. select row 4
6. panel on the right changes to 
    ```yaml
    key 1, key 2, key 3
    exp 1, 
    exp 2, ...
    ```
7. panel on the right turn into a parallel coordinate plot

- [ ] add multiple folder selection in the navbar to show experiments from those folders.

feature parity:

multi-key support for the `LineChart`? Need to be able to see all of the lines before selecting one or a few

so this is wild-card support in keys. In the input box, we putin a search query. it finds relevant keys
in the metric file before generating the plots.

- [ ] show grouped rows, organized by groupBy groupIgnore
- [ ] show 
- [x] fixed column width, use `hidden` for horizontal scroll inside cells
- [x] Drag and Drop column position
- [ ] organize the state, save column width to configuration.
    - widths: {key, width}
- [ ] resize column
- [ ] hide column
- [ ] add column (button, click and select/type and select)
- [ ] 
- [ ] order by column
- [ ] need to save column position
- [ ] minor point: editors need to support folding.
- [ ] add column width to keys
- [ ] column drag and drop: 
    https://github.com/ant-design/ant-design/issues/4639#issuecomment-316351389

- [x] chart row
- checkbox
- add and remove columns from table, with dropdown
- remove front page (redirect to /profiles)
- add image support
- compare results

New features:
- add header
- remove header
- order by column
- group by column


- resize
- row render
- infinite scroll

- [ ] window for adding the keys
- [ ] add multiKey support?? does it work now?
    - multi-key support already exist on the backend.
    - [x] need to add support in line chart.
- [ ] **Reach Feature Parity!!!!!!!**
- [ ] package for deployment
    - start vis app
    - start vis server (existing connection: local)
    - add configuration to turn off local config
    - add config for vis-only.
    - add file API

## Grid View


typical workflow:
> search for parameters, add filters to search to condense. (logger add start time and end time!)
- parameter search
- add experiment start and update time to parameters
- add view for experiment quick view

- [x] change toggle to hide first

### Urgent ToDos

- [ ] RC-table
    - scrollable support
    - full colSpan support
    - header click handle
    - column width
    

- allow removal of column names
- [ ] Need to add `startTime`, `endTime`, `length` to create
    - always add during experiment registration
    - for endTime, use metrics file __timestamp
    - If endTime large than 5 min, show stopped.
- add title bard to charts
- Allow adding charts to exp


### Rest Usability Issues

- [ ] add dates to directories (no need for now)
- [ ] add `load more` button to Directories
- allow reorder of column names via drag and drop
- add DATES to the NavBar
- add order (accent/decent) button to directories
- add delete button to Directories
- add rename button to Directories
- allow ordering by column
- allow grouping of columns (shift select)
- add `load more...` to the folders and files on the left.
- add search to `Directories (find)` and `Files (find)`. For `Experiments`, 

- Do not know what keys there are
- Do not know what metrics there are
- Would be good if we could order all experiments by dates. Starting from year, unfold by dates started

- At Project root, there are a lot of folders. Navbar only shows a few of them
- Need to be able to order the project folders
- Need to be able to navigate back to parent folder
- Need to support Images
- Need to support summary in table
- Want to be able to search
- Need to support sorting in table
- Need to add `startTime`, `endTime`, `length` to table for sorting
- use infinite list for table
- use draggable column width for table


- [ ] fix the trace ordering issue
- [ ] Change UI, to add table columns, with typeahead
- [ ] add title bar to chart
- [ ] next to title, add (...) button for modifying the chart config
- [ ] add in-line block to create chart
- [ ] add yaml encoding write

- [ ] table show metric results [need metrics query api, better to be single call]
- [ ] simple table component
- [ ] launch new vis server backend
- [ ] select charts to compare with each other
- [ ] `summary { 
        metricFiles: []
        prefix: string!
        key: string
        tail (n) {mean pc25 pc75 pc95 pc05 pc84 pc16 stddev mode}
        last
        }`

- **default values for `prefix`** key.
  the value for the prefix key should be the same to the current context
  and the relative paths should require a prefix key on the API side.
The powerful thing is that we can encapsulate these as react components.


- [ ] default unhide 3 expeirments in list view


- [x] implement end-point configuration
- [ ] deploy new visualization graphql server
- [ ] serve from the `./build` folder
- [ ] file container:
    - search in loaded list of files.
    - or search via query
- [ ] image scroller component
- [ ] video scroller component
- [ ] chart component with title

- [ ] **Comparison View**: Multiple Selection
- [ ] `parameters` field: 
    - [ ] hide row (place to the end?)
    - [ ] order by column
- [ ] add selection to table
- [ ] add chart to table row
- [ ] add row selector
- [ ] add delete button
- [ ] add comparison
- [ ] add image
- [ ] add video

- [ ] 

I need to focus on getting this dashboard to production ready.
- [ ] add range to plots
- [ ] comparison view (is this slow?)
- [ ] show figures in expanded list view
- [ ] chart builder
- in narrow viewport size, path#file? collapses into just file view. handle this inside the Dash module
- [x] write chat library in hooks 
- tab bar:
    - [x] create dash config
    - [x] get dash config
    - [x] edit dash config
    - [x] change to relay mutation
    - [x] get readme
    - [x] display Readme note
    - [x] show readme
    - [x] write readme
    - [ ] order by value (on client side)
    - [ ] make single file view
    - [ ] make first version of chart def.
    - [ ] show the first chart
    - [ ] show content of the dahsboard config file
    - [ ] create readme (client side only)
    - [ ] change readme filename (more involved)
    - [ ] Where to put the button for the README?
    
    - on the right: hamburger button to expand the dash configs
    - need `default.dashcfg` support
    - show `some_config.dashcfg`
    
    dash config supports multiple fines in the same yml configuration file.
    
- if is experiment: show experiment view in tab bar? or the same as the dash?
- search container
    > directory id
    > search query
    > experiments

    How is the experiments listed at the moment? (list *all* experiments under directory)

- [ ] result table (get aggregated slice from an averaged metric)
    - parameter keys
    - metric keys
- [ ] image component: epoch number
- [ ] video component: epoch number
- [ ] parameter table: define the API
- [ ] file-serving api: for image, video, and text.

> package these nicely, into some stand-along component that I can use.
- [ ] Advanced React Patterns:
    - ConnectionContainer: need to add search
    - ContextContainer
    - FragmentContainer
    - Getting Query Container to work with `found`
- [ ] Show an averaged plot
- [ ] frontend layout
- [ ] different views
- [ ] get bindr to work
- [ ] think of front end design
- [ ] add minimal front end
- [ ] get parallel coordinate to work
- [ ] get single chart to work

do these after the frontend is working
- [ ] actually return aggregated metric series
- [ ] add rolling average window

not working on.
- [ ] unify `project`, `directory`, and `experiment` with the same master type
- [ ] make the sample experiment 500MB large.
- [ ] navigate to child context
- [ ] make file explorer 
- [ ] setting up flow
- [ ] add mutation (for files)
- [ ] view queries in grahiQL
- [ ] make chart container
- [ ] copy experiment data

### Done

- [x] get first schema to run (file)
- [x] finish schema v0 
- [x] generate sample experiment records
- [x] finish relay tutorial
- [x] add routing
    > now with `farce` and `found`. 

- [x] add routing, start with user, expand to projects
    > main project, fork project etc.
    
- [x] break routes down
- [x] Add home page
- [x] add link to your own username
- [x] get user by username
- [x] add test?
- [x] list projects under user
- [x] add id to project
- [x] list directories under project
- [x] list directory under directory
- [x] list files under directory
- [x] list experiments under project
- [x] list directory under experiment
- [x] list files under experiment
- [x] list files under current context
- [x] flat keys for parameters
- [x] flat dictionary of parameters
- [x] metric files
- [x] metric file keys
- [x] metric file value query with keys
- [x] fix id to be absolute w.r.t `Args.logdir`
    > right now it is the server absolute path. 
    
    Now all uses `join(Args.logdir, self.id)`. We could replace this with a helper function.
- [x] add metric query to root query.
- [x] support queries with multiple metric files
- [x] CLEANUP: remove Starship starter code from the backend
- [x] add shim EditText mutation
- [x] Make sure that the client still works
- [x] wrap up and take a break.
- [x] break is over!
- [x] Parallel Coordinates
    Visualizations like this is not a magic bullet. I will still need to code up 
    the rest of the front-end to feature-parity.
- [x] show current project name
- [x] show current directory name
- [x] connection container directories
- [x] connection container for experiments
- [x] Build view components
    

---
- [x] File Browser
- [x] Experiment Row
- [x] Parameter Key Tags (and expanded view)
    > save as default.parameters
    > parameters: ["Args.lr", dict(name="some", domain=['some'])]
    > charts: ["some", "chart:chart-name"]
    **Aggregate**: choose `seed` to average? Need to key by *other* params first.
- [x] Show list of directories under current directory
- [x] Show list of experiments under current directory
    

- [x] make charts from table
- [x] grid view

- [x] change ExperimentDash to react hook
- [x] add selections box
- [x] get all selected rows
- [x] add toggle editDash
- [x] add toggle editReadme
- [x] add toggle showReadme

- [x] add **Inline Charts**
