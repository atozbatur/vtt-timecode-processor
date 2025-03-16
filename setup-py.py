from setuptools import setup, find_packages

setup(
    name="vtt-timecode-processor",
    version="1.0.0",
    description="A utility for processing WebVTT files and converting SRT to VTT",
    author="",
    author_email="",
    url="https://github.com/yourusername/vtt-timecode-processor",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "vtt-processor=vtt_processor:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: GUI",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing",
    ],
)
