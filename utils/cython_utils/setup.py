from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension('test_service', ['test_service.pyx'],
              language='c++')
]

setup(
    name='pets extensions',
    ext_modules=cythonize(extensions, language_level="3")
)
