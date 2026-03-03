from setuptools import setup, find_packages

setup(
    name="vyapar-saathi-backend",
    version="1.0.0",
    description="VyaparSaathi Lambda functions for demand forecasting",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "boto3>=1.28.0",
        "pandas>=2.0.3",
        "numpy>=1.25.0",
    ],
)
