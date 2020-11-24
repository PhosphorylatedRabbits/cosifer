"""Install package."""
import os
import subprocess
from setuptools import setup, find_packages, Command
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.develop import develop as _develop
from distutils.command.build import build as _build

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))


class setup_cosifer(Command):
    """
    Run installation of R dependencies.

    Run installation of R requirements used through rpy2.
    """

    description = 'Run script to setup COSIFER R dependencies'

    def initialize_options(self):
        """Set initialize options."""
        pass

    def finalize_options(self):
        """Set finalize options."""
        pass

    def run(self):
        """Run installation of R dependencies."""
        try:
            subprocess.check_call([
                os.path.join(SETUP_DIR, 'setup_cosifer.sh')
            ])
        except subprocess.CalledProcessError as error:
            raise EnvironmentError(
                f"Failed installion of R dependencies via {error.cmd}."
            )


class build(_build):
    """Build command."""

    sub_commands = [
        ('setup_cosifer', None)
    ] + _build.sub_commands


class bdist_egg(_bdist_egg):
    """Build bdist_egg."""

    def run(self):
        """Run build bdist_egg."""
        self.run_command('setup_cosifer')
        _bdist_egg.run(self)


class develop(_develop):
    """Build develop."""

    def run(self):
        """Run build develop."""
        setup_cosifer = self.distribution.get_command_obj(
            'setup_cosifer'
        )
        setup_cosifer.develop = True
        self.run_command('setup_cosifer')
        _develop.run(self)


scripts = ['bin/cosifer']

setup(
    name='cosifer',
    version='0.0.3',
    description='COSIFER - Consensus Interaction Network Inference Service',
    long_description=open('README.md').read(),
    url='https://github.com/PhosphorylatedRabbits/cosifer',
    author='Matteo Manica, Joris Cadow',
    author_email='drugilsberg@gmail.com, joriscadow@gmail.com',
    packages=find_packages('.'),
    cmdclass={
        'bdist_egg': bdist_egg,
        'build': build,
        'setup_cosifer': setup_cosifer,
        'develop': develop
    },
    install_requires=[
        'numpy',
        'scipy',
        'seaborn',
        'pandas<1.0',
        'scikit-learn',
        'statsmodels',
        'rpy2',
        'packaging',
        'pySUMMA @ git+https://github.com/learn-ensemble/PY-SUMMA'
    ],
    zip_safe=False,
    scripts=scripts
)
