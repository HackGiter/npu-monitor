import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="npu-monitor",  # 项目名称
    version="0.1.0",  # 项目版本
    author="HackGiter",  # 你的名字
    author_email="lee19990614@icloud.com",  
    description="A simple NPU monitoring tool.",  # 简短描述
    long_description=long_description, 
    long_description_content_type="text/markdown",  # 长描述的格式
    url="https://github.com/HackGiter/npu-monitor",  # 项目的 GitHub 仓库地址
    packages=setuptools.find_packages(),  # 自动查找项目中的包
    classifiers=[  # 项目的分类信息，用于 PyPI 搜索
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  # Python 最低版本要求
    entry_points={  # 定义可执行脚本
        'console_scripts': [
            'npu-monitor = npu_monitor.main:main',  # npu-monitor 命令对应 npu_monitor.main 模块中的 main 函数
        ],
    },
    install_requires=[],
    package_data={},
    include_package_data=True,
)