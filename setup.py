"""Package to convert arbitrary python objects into DTOs ready for serialization and validation."""

__version__ = "0.0.4"

from setuptools import setup, find_packages, Command

try:
    from mkdocs.main import main as mkdocs_main
except ImportError:
    def mkdocs_main(cmd, args, options):
        raise NotImplementedError("mkdocs modele must be installed to run this command.")

CLASSIFIERS = """
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: Public Domain
Programming Language :: Python
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries
Topic :: Software Development
""".strip().split("\n")


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
    author_email="send_me_spam@yahoo.com",
    url="https://github.com/nickswebsite/r2dto",
    version=__version__,
    description=__doc__,
    keywords="dto serializer serialize REST marshal JSON",
    packages=find_packages(exclude=["test/"]),
    cmdclass={
        "docs": DocsCommand,
    },
    classifiers=CLASSIFIERS,
)
