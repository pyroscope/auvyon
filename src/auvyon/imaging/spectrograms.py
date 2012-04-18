""" Audio data sample spectrograms.
"""
from __future__ import with_statement

import os
import sys
import tempfile
import subprocess
from contextlib import closing

from auvyon import config
from auvyon.audio import transcode


def spectrogram_image(mediafile, dpi=72, outdir=None, outfile=None):
    # TODO: Add some of the constants below as parameters
    """ Create spectrogram image from audio data.
        Return path to created image file.
    """
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt
    import scipy.io.wavfile
    import numpy as np
    import pylab

    # Output file path
    outfile = outfile or ""
    if outdir and outfile and os.sep in outfile:
        raise ValueError("Do not specify paths in both output directory '%s' and filename '%s'" % (outdir, outfile))

    if os.sep not in outfile:
        if not outfile:
            outfile = os.path.splitext(os.path.basename(mediafile))[0] + ".jpg"
        if not outdir:
            outdir = os.path.dirname(mediafile)
        outfile = os.path.join(outdir, outfile)

    with closing(open(os.devnull, "wb")) as black_hole:
        # Read audio data
        with transcode.to_wav(mediafile) as wavfile:
            sys.stdout, saved_stdout = black_hole, sys.stdout
            try:
                sample_rate, waveform = scipy.io.wavfile.read(wavfile)
            finally:
                sys.stdout = saved_stdout

        # Limit data to 10 second window from the middle, else the FFT needs ages
        data_window = sample_rate * 2 # secs
        waveform = [i[0] for i in waveform[(len(waveform) - data_window) // 2 : (len(waveform) + data_window) // 2]]
        # TODO: combine / add the channels to mono

        # Calculate FFT inputs
        nstep = int(sample_rate * 0.001) # 1ms step
        nfft = nwin = int(sample_rate * 0.005) & ~1 # 5ms window
        window = np.hamming(nwin)

        # Create spectrogram
        pylab.spectral()
        for khz in (5, 10, 16, 18, 20):
            pylab.text(data_window / sample_rate * .99, khz * 1000 + 75, "%d kHz" % khz, ha="right")
            pylab.axhline(khz * 1000)
        pylab.axis("off")
        pylab.specgram(waveform, NFFT=nfft, Fs=sample_rate, window=window)

        # Write to image
        try:
            pylab.savefig(outfile + ".png", format='png', facecolor="#000000", edgecolor="#000000", 
                dpi=dpi, transparent=True, bbox_inches="tight")

            cmd = [config.CMD_IM_CONVERT, "-trim", "-quality", "85", outfile + ".png", outfile]
            subprocess.check_call(cmd, stdout=black_hole, stderr=subprocess.STDOUT)
        finally:
            if os.path.exists(outfile + ".png"):
                os.remove(outfile + ".png")

    return outfile


def _main():
    """ Command line interface for testing.
    """
    if len(sys.argv) != 2:
        print("Usage: python -m auvyon.imaging.spectrograms <mediafile>")
    else:
        try:
            print("Created %s" % spectrogram_image(sys.argv[1], dpi=103, outfile="spectrogram.jpg"))
        except subprocess.CalledProcessError, exc:
            print("Conversion error: %s" % exc)


if __name__ == "__main__":
    _main()
