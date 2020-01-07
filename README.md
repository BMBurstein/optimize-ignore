# optimize-ignore
Tool to optimize large .gitignore (and similar) files.

I found that when working on a large codebase with lots of merges and lots of `.gitignore` changes written both manually and by "ignore this file" type of commands in the IDE, the `.gitignore` file tends to get very large with lots of duplicate or overlapping rules. This tool is my attempt at using huristics to optimize it.
