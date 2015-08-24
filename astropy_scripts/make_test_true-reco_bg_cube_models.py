from __future__ import (absolute_import, division, print_function,
                        unicode_literals) # python 2 as python 3
import os
from astropy.units import Quantity
from astropy.coordinates import Angle
from astropy.time import Time
from gammapy.datasets import make_test_bg_cube_model, make_test_dataset
from gammapy.scripts import make_bg_cube_models

TEST = True
#TEST = False

CLEAN_WORKING_DIR = 1 # remove existing observation and bg cube model files

# using half hard-coded values from scripts.group_observations
AZ_RANGE = Angle([90, 270], 'degree')
ALT_RANGE = Angle([72, 90], 'degree')
GROUP_ID = 27
if TEST:
    AZ_RANGE = Angle([90, 270], 'degree')
    ALT_RANGE = Angle([45, 90], 'degree')
    GROUP_ID = 1
OUTDIR = 'bg_cube_models'
OVERWRITE = False

def make_true_model():
    """Make a true bg cube model."""

    # use hard coded binning in CubeBackgroundModel.define_cube_binning
    detx_range = (Angle(-0.07, 'radian').to('degree'),
                  Angle(0.07, 'radian').to('degree'))
    ndetx_bins = 60
    dety_range = (Angle(-0.07, 'radian').to('degree'),
                  Angle(0.07, 'radian').to('degree'))
    ndety_bins = 60
    energy_band = Quantity([0.1, 80.], 'TeV')
    nenergy_bins = 20

    # average altitude
    # TODO: should it be average from the cosinus???!!!
    altitude = (ALT_RANGE[0]+ ALT_RANGE[1])/2.

    # using half hard-coded values (default from make_test_eventlist)
    sigma = Angle(5., 'deg'),
    spectral_index = 2.7,

    overwrite = OVERWRITE

    bg_cube_model = make_test_bg_cube_model(detx_range=detx_range,
                                            ndetx_bins=ndetx_bins,
                                            dety_range=dety_range,
                                            ndety_bins=ndety_bins,
                                            energy_band=energy_band,
                                            nenergy_bins=nenergy_bins,
                                            altitude= altitude,
                                            apply_mask=False)

    # create output folder
    outdir = OUTDIR + '_true'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    else:
        if overwrite:
            # delete and create again
            shutil.rmtree(outdir) # recursively
            os.mkdir(outdir)
        else:
            # do not overwrite, hence exit
            s_error = "Cannot continue: directory \'{}\' exists.".format(outdir)
            raise RuntimeError(s_error)

    # save
    group_id = GROUP_ID
    outfile = outdir + '/bg_cube_model_group{}'.format(group_id)
    print("Writing {}".format('{}_table.fits.gz'.format(outfile)))
    print("Writing {}".format('{}_image.fits.gz'.format(outfile)))
    bg_cube_model.write('{}_table.fits.gz'.format(outfile),
                        format='table', clobber=overwrite)
    bg_cube_model.write('{}_image.fits.gz'.format(outfile),
                        format='image', clobber=overwrite)


def make_reco_model():
    """Make a reco bg cube model."""

    SCHEME = 'HESS'
    METHOD = 'default'

    fits_path = 'test_dataset'
    overwrite = OVERWRITE
    test = TEST

    # 1. create dummy dataset

    observatory_name = SCHEME

    # use enough stats so that rebinning (and resmoothing?) doesn't take place
    n_obs = 100
    if test:
        # run fast
        n_obs = 2

    az_range = AZ_RANGE
    alt_range = ALT_RANGE

    make_test_dataset(fits_path=fits_path, overwrite=overwrite,
                      observatory_name='HESS', n_obs=n_obs,
                      az_range=az_range,
                      alt_range=alt_range,
                      date_range=(Time('2010-01-01T00:00:00',
                                       format='isot', scale='utc'),
                                  Time('2015-01-01T00:00:00',
                                       format='isot', scale='utc')),
                      n_tels_range=(3, 4),
                      random_state='random-seed')

    # 2. build bg model

    outdir = OUTDIR + '_reco'
    scheme = SCHEME
    method = METHOD
    make_bg_cube_models(fitspath=fits_path, scheme=scheme,
                        outdir=outdir, overwrite=overwrite,
                        test=test, method=method)

def compare_models():
    """Compare data/binning in both models with a few asserts."""
    # TODO!!!


def plot_comparison():
    """Compare data in both models with a few plots."""
    # TODO!!! use/emulate plot_bg_cube_model_comparison.py !!!


if __name__ == '__main__':

    # remove old files
    if CLEAN_WORKING_DIR:
        print("Cleaning working dir.")
        command = "rm test_dataset/ bg_cube_models_true/ bg_cube_models_reco/ -fr"
        print(command)
        os.system(command)

    make_true_model()
    make_reco_model()
    compare_models()
    plot_comparison()
