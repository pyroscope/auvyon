""" Transcode audio formats.
"""
from __future__ import with_statement

import os
import tempfile
import subprocess
from contextlib import contextmanager

from auvyon import config


def extract_wav(datafile, target=None):
    """ Get LPCM 16bit audio stream from mediafile.
    
        If `target` is a directory, create a .wav with the same basename as the input.
        If target is empty, write to the directory of the source file. Otherwise, use it 
        directly as the target filename.
    """
    if datafile.endswith(".wav"):
        return datafile

    target = target or os.path.dirname(datafile) 
    if os.path.isdir(target):
        target = os.path.join(target, os.path.splitext(os.path.basename(datafile))[0] + ".wav")

    if datafile.endswith(".flac"):
        cmd = [config.CMD_FLAC, "--silent", "--decode", "--force", "-o", target, datafile]
    else:
        cmd = [config.CMD_FFMPEG, "-v", "0", "-y", "-i", datafile, "-acodec", "pcm_s16le", "-ac", "2", target]
    subprocess.check_call(cmd, stdout=open(os.devnull, "wb"), stderr=subprocess.STDOUT)

    return target


@contextmanager
def to_wav(mediafile):
    """ Context manager providing a temporary WAV file created from the given media file.
    """
    if mediafile.endswith(".wav"):
        yield mediafile
    else:
        wavfile = tempfile.mktemp(__name__) + ".wav"
        try:
            extract_wav(mediafile, wavfile)
            yield wavfile
        finally:
            if os.path.exists(wavfile):
                os.remove(wavfile)
