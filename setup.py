import os
from setuptools import setup, find_packages

setup(
    name='scons-project',
    version='0.1',
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    url='https://github.com/furious-luke/scons-project',
    description='Common build structure for C/C++ projects.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: SCons',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    license='BSD',

    packages=find_packages(),
    scripts=['sconsproject/scripts/scons-project'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
)
