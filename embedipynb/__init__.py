""" Embed graphics into Ipynb notebook Exporter class. Contains code from
    nbconvert and jupyter-contrib-nbextensions embedded.
"""

import base64
import os
import re

try:
    from urllib.request import urlopen  # py3
except ImportError:
    from urllib2 import urlopen

from nbconvert.exporters.exporter import Exporter
import nbformat
from traitlets import Enum, default, Bool, Unicode
from ipython_genutils.ipstruct import Struct
from nbconvert.preprocessors import Preprocessor

class EmbedImagesInIpynbPreprocessor(Preprocessor):
    """
    The preprocessor that embed local images in a notebook itself.
    """

    def preprocess(self, nb, resources):
        """Skip preprocessor if not enabled"""
        nb, resources = super(EmbedImagesInIpynbPreprocessor, self).preprocess(nb, resources)
        return nb, resources


    def replfunc_md(self, match):
        """Read image in markdown and store as base64 encoded attachment"""
        url = match.group(2)
        imgformat = url.split('.')[-1].lower()
        if url.startswith('http'):
            if self.embed_remote_images:
                data = urlopen(url).read()
            else:
                return match.group(0)
        elif url.startswith('attachment'):
            return match.group(0)
        else:
            filename = os.path.join(self.path, url)
            with open(filename, 'rb') as f:
                data = f.read()

        if self.resize in self.imgsizes.keys():
            data = self.resize_image(url, imgformat, data)

        self.log.debug("Embedding url: %s, format: %s" % (url, imgformat))
        b64_data = base64.b64encode(data).decode("utf-8")
        self.attachments[url] = {'image/' + imgformat: b64_data}

        newimg = '![' + match.group(1) + '](attachment:' + match.group(2) + ')'
        return newimg

    def replfunc_img(self, match):
        """Read image in HTML fragment and embed as base64"""
        url = match.group(1)
        print(url)
        imgformat = url.split('.')[-1].lower()
        b64_data = None
        prefix = None

        if imgformat not in ['jpg', 'png', 'gif', 'jpeg', 'bmp', 'svg', 'pdf']:
            return match.group(0)

        if url.startswith('data'):
            return match.group(0);  # Already in base64 Format

        if url.startswith('http'):
            if self.embed_remote_images:
                data = urlopen(url).read()
            else:
                return match.group(0)
        elif url.startswith('attachment'):
            return match.group(0)
        else:
            filename = os.path.join(self.path, url)
            with open(filename, 'rb') as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")
                if imgformat == "svg":
                    prefix = "data:image/svg+xml;base64,"
                elif imgformat == "pdf":
                    prefix = "data:application/pdf;base64,"
                else:
                    prefix = "data:image/" + imgformat + ';base64,'
            return "src=\"" + prefix + b64_data + "\""

    def preprocess_cell(self, cell, resources, index):
        """
        Preprocess cell

        Parameters
        ----------
        cell : NotebookNode cell
            Notebook cell being processed
        resources : dictionary
            Additional resources used in the conversion process.
        index : int
            Index of the cell being processed (see base.py) Not used.
        """
        self.path = resources['metadata']['path']
        self.attachments = getattr(cell, 'attachments', Struct())

        if cell.cell_type == "markdown":
            regex = re.compile('!\[([^"]*)\]\(([^"]+)\)')
            otherregex = re.compile('src\s*=\s*\"([^"]+)\"')
            cell.source = regex.sub(self.replfunc_md, cell.source)
            cell.source = otherregex.sub(self.replfunc_img, cell.source)
            cell.attachments = self.attachments
        return cell, resources

class EmbedImagesInIpynbExporter(Exporter):
    """Takes a IPython notebook, and looks at what images it references. If
    they are local, they are embedded in the notebook itself.

    As a command line parameter when calling NbConvert::

        $ jupyter nbconvert --to embedipynb  mynotebook.ipynb

    This exporter was designed for loading IPython notebooks in the
    Mezzanine CMS when they contain references to local images. Rather than
    load the images separately, it was thought to be easier to combine the
    images and the notebook together.
    """
    preprocessors=[EmbedImagesInIpynbPreprocessor]
    nbformat_version = Enum(list(nbformat.versions),
        default_value=nbformat.current_nbformat,
        help="""The nbformat version to write.
        Use this to downgrade notebooks.
        """
    ).tag(config=True)

    @default('file_extension')
    def _file_extension_default(self):
        return '.ipynb'

    output_mimetype = 'application/json'

    def from_notebook_node(self, nb, resources=None, **kw):
        nb_copy, resources = super(EmbedImagesInIpynbExporter, self).from_notebook_node(nb, resources, **kw)
        if self.nbformat_version != nb_copy.nbformat:
            resources['output_suffix'] = '.v%i' % self.nbformat_version
        else:
            resources['output_suffix'] = '.nbconvert'
        output = nbformat.writes(nb_copy, version=self.nbformat_version)
        if not output.endswith("\n"):
            output = output + "\n"
        return output, resources
