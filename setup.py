from setuptools import setup, find_packages

setup(
    name="domain-checker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-whois==0.8.0",
        "requests==2.31.0",
        "tabulate==0.9.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "domain-checker=domain_checker.main:main",
        ],
    },
    author="Giorgio Giannone",
    author_email="your.email@example.com",
    description="A tool to check domain name availability",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gegianno/domain-checker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 