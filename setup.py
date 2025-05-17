
from setuptools import setup, find_packages

setup(
    name="pomodoro_timer",
    author="Vladimir Podlevskikh",
    author_email="pip@podlevskikh.com",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pygame",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pomodoro_timer = pomodoro.main:main",
        ],
    },
)

