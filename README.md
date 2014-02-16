Grimlock
========

["Me, Grimlock."](http://tfwiki.net/wiki/Grimlock_(G1))

A simple transformation/data processing pipeline for CrisisNET. Pulls jobs from a FIFO queue and runs each through a series of predefined tasks. These tasks add metadata to content retrieved by [Sucka](https://github.com/ushahidi/sucka).

New tasks can be added to the `tasks` package, and included in the pipeline in `app.set_pipeline_steps`. 

Very much a work in progress. Watch this space.
