# embedipynb
Takes a IPython notebook, and looks at what images it references. If they are
local, they are embedded in the notebook itself. To install:

    $ python setup.py install

To execute:

    $ jupyter nbconvert --to embedipynb  mynotebook.ipynb

This exporter was designed for loading IPython notebooks in the
Mezzanine CMS when they contain references to local images. Rather than
load the images separately, it was thought to be easier to combine the
images and the notebook together.
