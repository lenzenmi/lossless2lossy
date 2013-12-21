from distutils.core import setup

setup(
    name="lossless2lossy",
    version="1.0.0",
    packages=['lossless2lossy'],
    scripts=['scripts/lossless2lossy'],

    # metadata for upload to PyPI
    author="Mike Lenzen",
    author_email="lenzenmi@gmail.com",
    description="A program to simplify working with BTRFS snapshots.",
    license="GPL3",
    keywords=("flac", "mp3", "music"),
    url="",  # project home page, if any
)
