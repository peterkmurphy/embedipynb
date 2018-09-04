from setuptools import setup

setup(name='embedipynb',
      version='0.1',
      description='Embeds images in Jupyter/iPython notebooks',
      url='https://github.com/peterkmurphy/embedipynb',
      author='Peter Murphy',
      author_email='peterkmurphy@gmail.com',
      license='BSD 3-Clause',
      packages=['embedipynb'],
      zip_safe=False,
      entry_points = {
        'nbconvert.exporters': [
            'embedipynb = embedipynb:EmbedImagesInIpynbExporter'
        ],
     }
)
