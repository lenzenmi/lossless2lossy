==============
lossless2lossy
==============

.. contents::

A command line utility that automates the task of maintaining a lossy encoded copy of your lossless music for use on portable devices.

Features
--------

* maintains a mirrored directory structure
* encodes lossless formats to a specified lossy format
* copies lossy files without transcoding
* copies albumart
* utilizes all available processing cores


Supported Formats
~~~~~~~~~~~~~~~~~

**lossless formats:**
    * flac -> https://xiph.org/flac/
        + high quality re-sampling for sampling frequencies above 44.1khz

**lossy formats:**
    * mp3 -> http://lame.sourceforge.net/
        + replaygain analyzed and applied
        + ID3 v1.1 and 2.4 applied
    

Installation
------------

Before installing lossless2lossy, you will need to install 3rd party packages and ensure they are available on your system path.

Required System Packages
~~~~~~~~~~~~~~~~~~~~~~~~
:Name: lame
:URL: http://lame.sourceforge.net/

----

:Name: flac
:URL: https://xiph.org/flac/

----

:Name: sox
:URL: http://sox.sourceforge.net/

----

:Name: mp3gain
:URL: http://mp3gain.sourceforge.net

----

:Name: python2-eyed3
:URL: http://eyed3.nicfit.net/

Required Python Packages
~~~~~~~~~~~~~~~~~~~~~~~~
mutagenx

The easiest way to install python packages is to use ``pip``::

    pip install -r requirements.txt
    
Installing lossless2lossy
~~~~~~~~~~~~~~~~~~~~~~~~~
Once all of the dependencies are installed simply do::

    python setup.py install
    
Usage
-----

::

    lossless2lossy --delete {format} source encoded

where::

    --delete    (optional) if specified all files that are not present in the source folder
                will be deleted from the encoded folder
 
    {format}    (optional default=mp3) choose the format to encode to
    
    source      (required) path to the lossless files
    
    encoded     (required) path where the encoded files will be saved

Example
~~~~~~~
::
    
    lossless2lossy --delete /home/music/flac/ /home/music/mp3/    
    
