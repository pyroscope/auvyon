""" Audio data visualization.
"""
from __future__ import with_statement

import os
import sys
import shlex
import shutil
import tempfile
import subprocess

from auvyon import config
from auvyon.audio import transcode


# Default colors (RGBA)
WAVE_CENTER_COLOR = (0x00, 0xbb, 0x11, 0xff)
WAVE_OUTER_COLOR  = (0x99, 0x00, 0x11, 0xff)
WAVE_BG_COLOR     = (0x11, 0x11, 0x33, 0xff)
WAVE_LABEL_STYLE  = "-background '#333366ff' -stroke '#fff' -font DejaVu-Sans-ExtraLight -pointsize 12"


def waveform_image(mediafile, xy_size, outdir=None, center_color=None, outer_color=None, bg_color=None):
    """ Create waveform image from audio data.
        Return path to created image file.
    """
    try:
        import waveform
    except ImportError, exc:
        raise ImportError("%s [get it at https://github.com/superjoe30/PyWaveform]" % exc)

    outdir = outdir or os.path.dirname(mediafile)
    outfile = os.path.join(outdir, os.path.splitext(os.path.basename(mediafile))[0] + ".png")

    with transcode.to_wav(mediafile) as wavfile:
        # Draw using a gradient
        waveform.draw(wavfile, outfile, xy_size, 
            bgColor=bg_color or WAVE_BG_COLOR,
            fgGradientCenter=center_color or WAVE_CENTER_COLOR, 
            fgGradientOuter=outer_color or WAVE_OUTER_COLOR)

    return outfile


def waveform_stack(mediafiles, xy_size, output=None, label_style=None, 
        center_color=None, outer_color=None, bg_color=None):
    """ Create a stack of waveform images from audio data.
        Return path to created image file.
    """
    img_files = []
    output = output or os.path.abspath(os.path.dirname(os.path.commonprefix(mediafiles)))
    if os.path.isdir(output):
        output = os.path.join(output, "waveforms.jpg")
    cmd = [config.CMD_IM_MONTAGE] + shlex.split(label_style or WAVE_LABEL_STYLE)
    cmd += ["-tile", "1x%d" % len(mediafiles), "-geometry", "%dx%d" % xy_size, "-label", "%t"]

    try:
        tempdir = tempfile.mktemp(__name__)
        os.makedirs(tempdir) 

        for mediafile in sorted(mediafiles):
            img_files.append(waveform_image(mediafile, xy_size, tempdir, center_color, outer_color, bg_color))

        cmd.extend(img_files)
        cmd.append(output)
        subprocess.check_call(cmd, stdout=open(os.devnull, "wb"), stderr=subprocess.STDOUT)
    finally:
        if os.path.isdir(tempdir):
            shutil.rmtree(tempdir, ignore_errors=True)

    return output


def _main():
    """ Command line interface for testing.
    """
    if len(sys.argv) <= 1:
        print("Usage: python -m auvyon.imaging.waveforms <mediafile>...")
    else:
        try:
            print("Created %s" % waveform_stack(sys.argv[1:], (640, 48)))
        except subprocess.CalledProcessError, exc:
            print("Conversion error: %s" % exc)


if __name__ == "__main__":
    _main()
