from setuptools import setup, find_packages

setup(
    name="codegate",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-generativeai>=0.3.0",
        "rich>=13.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "aiofiles>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "codegate=codegate.cli.repl:main",
        ],
    },
)
