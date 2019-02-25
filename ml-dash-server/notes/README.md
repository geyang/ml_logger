# Implementation Plans

1. build schema
2. make single dataview 
3. make file-list view
4. make diff view
5. make layout
6. make chart key view
7. single experiment view?

## ToDos

- [ ] show current project name
- [ ] show current directory name
- [ ] connection container directories
- [ ] connection container for experiments
- [ ] Show list of directories under current directory
- [ ] Show list of experiments under current directory
- [ ] Advanced React Patterns:
    - ContextContainer
    - FragmentContainer
    - Getting Query Container to work with `found`
- [ ] Build view components
- [ ] parameter table
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
    

---
- [ ] File Browser
- [ ] Experiment Row
- [ ] Parameter Key Tags (and expanded view)
    > save as default.parameters
    > parameters: ["Args.lr", dict(name="some", domain=['some'])]
    > charts: ["some", "chart:chart-name"]
    **Aggregate**: choose `seed` to average? Need to key by *other* params first.
    

