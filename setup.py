from setuptools import setup, find_packages

setup(
    name="ai_project_helper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "protobuf",
        "requests",
        "pyyaml"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    description="LLM-powered DevOps automation agent with streaming gRPC feedback.",
    author="Teryfly",
    entry_points={
        "console_scripts": [
            "ai_project_helper-server=ai_project_helper.server:serve"
        ]
    },
)
