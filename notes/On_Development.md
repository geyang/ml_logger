# Notes for Developing `ml-logger`

There are some of the collateral damages of developing this module.

## Specifying the packages inside `setup.py`

:link:[Traps for the Unwary in Python’s Import System](http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html)

Python's stupid module system requires that your `setup.py` specify **all** modules that are to be included. One usually don't really this is needed until he/she has spent ten minutes digging through a missle sub-module in a published version of the package.

There are different ways to handle this, this is just a note that you need to pay attention to this if you create new submodules.

```python
# setup.py
      packages=[
          "ml_logger",
          "ml_logger.caches",
          "ml_logger.helpers",  # and who needs a closing bracket?
```
