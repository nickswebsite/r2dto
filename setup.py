__version__ = "0.0.1"

from setuptools import setup, find_packages, Command

try:
    from mkdocs.main import main as mkdocs_main
except ImportError:
    def mkdocs_main(cmd, args, options):
        raise NotImplementedError("mkdocs modele must be installed to run this command.")


class DocsCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        mkdocs_main("build", (), {"clean": True})


setup(
    name="r2dto",
    author="The Magnificant Nick",
    version=__version__,
    packages=find_packages(exclude=["test/"]),
    cmdclass={
        "docs": DocsCommand,
    }
)
