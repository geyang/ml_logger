### Pages:

- Profile
- Project
- Dash


#### Dash View Specifications

- [ ] Left Bar
    1. quick selection
        Show number of experiments
    2. dash
    3. experiments

- [ ] Experiment View (Originally List View)
    - Experiment Name
    - tab bar
        Choosing from Multiple Parameter Key configs
            `[ > config name | key_1 | key_2 ... | input-box | ⬇️ ]`
    - parallel coordinates?
    - experiment list

    You can expand the experiment list to show details of all of the experiments
- [ ] Details Pane
    - tab bar (the name of the view gets saved)
    - Details of the visualization

---

- [ ] Experiment View (Originally List View)
    0. default view:
        - left nav bar collapses into 56 px wide, also being used as selection bar
        - Initially just 800 px wide. Expand once more charts are added.
        - Initially Grid View, List View After. 
        - Grid View sub charts arranged in views
        - selection box on left, entire vertical span
        > **old idea** show parameter table, animate expand to full list view, show keys containing `loss`, 
        `success`, `acuracy` then others by default
    1. On selection:
        When an experiment is selected, show (add to quick selection) in the tab bar (top)
        - Show "Selection" in tab bar
        - flash "quick selection" in nav bar.
        - quick selection is the global bin, saved under project root.
            To view quick selections, go to project root
        - show parameter table in expanded tab bar
        
        When two experiments are selected, expand tab, highlight `selection` tab, show plot overlay
        
        - Show (expand view) on the right of each experiment block/row. Allow detailed view on the right split-view
    2. Tab View:
        - Show filter fields (used to specify parallel coordinates)
        - Underneath, show parallel coordinates
        
- [ ] Choosing from Multiple Parameter Key configs
    `[ > config name | key_1 | key_2 ... | input-box | ⬇️ ]`
- [ ] Project View:
    - Now a list of experiments/dashboards
    - + quick selection
- [ ] Experiment View (Originally List View)
    0. default view:
        - left nav bar collapses into 56 px wide, also being used as selection bar
        - Initially just 800 px wide. Expand once more charts are added.
        - Initially Grid View, List View After. 
        - Grid View sub charts arranged in views
        - selection box on left, entire vertical span
        > **old idea** show parameter table, animate expand to full list view, show keys containing `loss`, 
        `success`, `acuracy` then others by default
    1. On selection:
        When an experiment is selected, show (add to quick selection) in the tab bar (top)
        - Show "Selection" in tab bar
        - flash "quick selection" in nav bar.
        - quick selection is the global bin, saved under project root.
            To view quick selections, go to project root
        - show parameter table in expanded tab bar
        
        When two experiments are selected, expand tab, highlight `selection` tab, show plot overlay
        
        - Show (expand view) on the right of each experiment block/row. Allow detailed view on the right split-view
    2. Tab View:
        - Show filter fields (used to specify parallel coordinates)
        - Underneath, show parallel coordinates
- [ ] Single Experiment View
    1. No params vis on top
    2. Show different dashboard (inherit from top, allow override)
        Expand out to full grid
    3. save view in `default.dashcfg`
- [ ] Left Bar
    1. quick selection
        Show number of experiments
    2. dash
    3. experiments
