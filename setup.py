from setuptools import setup, find_packages

setup(
    name='tau_performance',
    version='0.0.1',
    description='',
    url='',
    author=['Laurits Tani, Riccardo Manzoni, Dennis Roy'],
    author_email='laurits.tani@cern.ch',
    license='GPLv3',
    python_requires='>3.6.0',
    packages=find_packages(),
    package_data={
        'tau_performance': [
            'scripts/*'
        ]
    }
)
