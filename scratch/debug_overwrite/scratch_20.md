
# Debug Logger Overwrite Bug

Reading from metrics file:

```
http://54.71.92.65:8080
```

```ansi
══════════════════════════════════════════
[33m        run         [0m
────────────────────┬─────────────────────
     createTime     │ 2021-01-23 02:39:14.259214-05:00
       prefix       │ geyang/project/debug_logs
════════════════════╧═════════════════════
╒════════════════════╤════════════════════════════╕
│         i          │             0              │
├────────────────────┼────────────────────────────┤
│      timestamp     │'2021-01-23T07:39:14.591506'│
╘════════════════════╧════════════════════════════╛

╒════════════════════╤════════════════════╕
│         i          │         1          │
╘════════════════════╧════════════════════╛

╒════════════════════╤════════════════════╕
│         i          │         2          │
╘════════════════════╧════════════════════╛


```
```python
data = logger.read_metrics()
doc.print(data)
```

```
   i                __timestamp
0  1 2021-01-23 07:39:14.594227
1  0 2021-01-23 07:39:14.591506
2  2 2021-01-23 07:39:14.596020
```