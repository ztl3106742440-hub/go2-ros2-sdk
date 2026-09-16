from setuptools import find_packages, setup


setup(
    name="go2-module1",
    version="0.1.0",
    description="Pure unitree_sdk2_python course framework for Go2 EDU",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.10",
)

