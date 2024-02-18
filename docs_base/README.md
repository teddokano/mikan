# "mikan" docs folder

This folder help to generate docstring document. 
HTML documents will be generated in docs/\*.html after executing following commands in mikan's top folder.  

`sphinx-apidoc -f -o ./docs_base .`  
`sphinx-build ./docs_base ./docs`

To re-build the documents,to be sure the Sphinx and theme are installed properly (by `$ pip install -U --pre sphinx` and `pip install sphinx-rtd-theme`). 
