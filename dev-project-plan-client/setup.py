from setuptools import setup, find_packages

setup(
    name="plan_manager",
    version="0.1.0",
    description="Software Development Plan Management Program",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pymysql",
        "grpcio",
        "grpcio-tools"
    ],
    python_requires='>=3.8',
    entry_points={
        "console_scripts": [
            "plan-manager=plan_manager.main:main"
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.ini"]
    }
)