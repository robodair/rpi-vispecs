from setuptools import setup

setup(name='vispecs',
      version='1.0.0.dev3',
      description='Python package for rainforest spectrum sensors',
      long_description=open('README.md').read(),
      url='https://github.com/alisdairrobertson/rpi-vispecs',
      author='Alisdair Robertson',
      author_email='alisdairrobertson@github.com',
      license='All Rights Reserved',
      packages=['vispecs'],
      install_requires=['picamera', 'h5py'],
      zip_safe=False)
