
from setuptools import setup, find_packages

setup(
    name="pomodoro_timer",
    author="Vladimir Podlevskikh",
    author_email="pip@podlevskikh.com",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=2.0.0,<3.0.0",
        "pygame>=2.6.0,<3.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pomodoro_timer = pomodoro.main:main",
        ],
    },
)

