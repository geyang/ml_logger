# Implementation Plans

1. build schema
2. make single dataview 
3. make file-list view
4. make diff view
5. make layout
6. make chart key view
7. single experiment view?

## ToDos

**Reach Feature Parity!!!!!!!**

## Grid View

```yaml
charts:
- series:
  - metricFiles: ['experiment_00/metrics.pkl', 'experiment_01/metrics.pkl']
    prefix: 'episodeyang/playground/mdp'
    xKey: __timestamp
    yKey: sine
    interpolation: null
    k: 100  # the number of points to return
```

- [ ] change ExperimentDash to react hook
- [ ] **Comparison View**: Multiple Selection
- [ ] **Inline Charts**
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
