from pathlib import Path

from setuptools import find_packages, setup


requirements = [
    line.strip()
    for line in Path("requirements.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]


setup(
    name="analisi-nuoto",
    version="0.1.0",
    description="Pipeline per analizzare dati di nuoto esportati in CSV.",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "analisi_nuoto=analisi_nuoto.cli:main",
        ],
    },
)
