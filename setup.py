from os.path import dirname, abspath

from setuptools import setup


requirements_file = dirname(abspath(__file__)) + "/requirements.txt"
with open(requirements_file, "r") as f:
    requirements = f.read().splitlines()

setup(
    name="calculator-bot",
    version="2.0.2",
    packages=["calculator_bot"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "calculator-bot = calculator_bot.app:main",
        ],
    },
    include_package_data=True,
)
