from __future__ import (absolute_import, division, print_function,
                        unicode_literals) # python 2 as python 3
from tempfile import NamedTemporaryFile
import numpy as np
from numpy.testing import assert_allclose
import matplotlib.pyplot as plt
from astropy.units import Quantity
from astropy.coordinates import Angle
from gammapy.background import CubeBackgroundModel
from gammapy import datasets
from gammapy_bg_models_utilities import CubeBackgroundModelUtils as CBMutils
from gammapy.datasets.make import make_test_bg_cube_model

GRAPH_DEBUG = 0
USE_TEMP_FILES = 0
CACHE = 1 # set to 0 to ignore downloaded files in the cache
          # (or use rm ~/.astropy/cache)

def cube_bg_model_plots(filename):
    """Plot background model and store as cube so that it can viewed with ds9.
    """
    bg_model = CubeBackgroundModel.read(filename, format='table')

    ##bg_model.plot_images() # old code
    CBMutils.plot_images(bg_model)
    CBMutils.plot_images(bg_model, energy=Quantity(2., 'TeV'))
    #bg_model.plot_image(energy=Quantity(1., 'TeV'))
    bg_model.plot_image(energy=Quantity(2., 'TeV'))
    #bg_model.plot_image(energy=Quantity(3., 'TeV'))
    #bg_model.plot_image(energy=Quantity(1.53216636, 'TeV'))
    #bg_model.plot_image(energy=Quantity(2.27553916, 'TeV'))
    #bg_model.plot_image(energy=Quantity(80., 'TeV'))
    #bg_model.plot_image(energy=Quantity([1.], 'TeV'))
    #bg_model.plot_image(energy=Quantity([2.], 'TeV'))
    #bg_model.plot_image(energy=Quantity([1., 2.], 'TeV'))

    ##bg_model.plot_spectra() # old code
    CBMutils.plot_spectra(bg_model, format='mosaic')
    CBMutils.plot_spectra(bg_model, format='stack')
    CBMutils.plot_spectra(bg_model, det=Angle([0., 0.], 'degree'))
    bg_model.plot_spectrum(det=Angle([0., 0.], 'degree'))
    #bg_model.plot_spectrum(det=Angle([0., 2.], 'degree'))
    #bg_model.plot_spectrum(det=Angle([-5., 0.], 'degree'))
    #bg_model.plot_spectrum(det=Angle([0., -5.], 'degree'))
    #bg_model.plot_spectrum(det=Angle([-5., -5.], 'degree'))
    #bg_model.plot_spectrum(det=Angle([[0., 0.]], 'degree'))
    #bg_model.plot_spectrum(det=Angle([[0., 0.], [1., 1.]], 'degree'))

    outfile = 'cube_background_model.fits'
    bg_model.write(outfile, format='image', clobber=True) # overwrite


def test_cube_bg_model_class(filename):
    """Testing the tests for gammapy.
    """
    # test shape of bg cube when reading a file
    bg_cube_model = CubeBackgroundModel.read(filename, format='table')
    print("bg_cube_model.background.shape", bg_cube_model.background.shape)
    print("len(bg_cube_model.background.shape)", len(bg_cube_model.background.shape))
    assert len(bg_cube_model.background.shape) == 3
    assert bg_cube_model.background.shape == (len(bg_cube_model.energy_bins) - 1,
                                              len(bg_cube_model.dety_bins) - 1,
                                              len(bg_cube_model.detx_bins) - 1)

    # example how to access data in cube
    # TODO: are axis (X, Y) correct?!!!
    #       need a test with asymmetric number of bins in X/Y!!!
    energy_bin = bg_cube_model.find_energy_bin(energy=Quantity(2., 'TeV'))
    det_bin = bg_cube_model.find_det_bin(det=Angle([0., 0.], 'degree'))
    bg_cube_model.background[energy_bin, det_bin[0], det_bin[1]]

    # test image plot:
    # test bg rate values plotted for image plot of energy bin conaining E = 2 TeV
    energy = Quantity(2., 'TeV')
    ax_im = bg_cube_model.plot_image(energy)
    plt.draw()
    if GRAPH_DEBUG:
        plt.show() # wait until image is closed
    # get plot data (stored in the image)
    image_im = ax_im.get_images()[0]
    plot_data = image_im.get_array()
    # I need also the bin ids!!!
    plot_shape = image_im.get_array().shape
    plot_extent = image_im.get_extent()
    print("plot data")
    print(plot_data)
    print("plot shape", plot_shape)
    print("plot extent", plot_extent)

    # get data from bg model object to compare
    energy_bin = bg_cube_model.find_energy_bin(energy)
    model_data = bg_cube_model.background[energy_bin]
    # TODO: get also det (x,y coord) of the bins!!!
    print("model data")
    print(model_data)

    # test if both arrays are equal
    assert_allclose(plot_data, model_data.value)

    # test spectrum plot:
    # test bg rate values plotted for spectrum plot of detector bin conaining det (0, 0) deg (center)
    det = Angle([0., 0.], 'degree')
    #det = Angle([0., 2.], 'degree')
    ax_spec = bg_cube_model.plot_spectrum(det)
    plt.draw()
    if GRAPH_DEBUG:
        plt.show() # wait until image is closed
    # get plot data (stored in the line)
    plot_data = ax_spec.get_lines()[0].get_xydata()
    print("plot data")
    print(plot_data)

    # get data from bg model object to compare
    det_bin = bg_cube_model.find_det_bin(det)
    model_data = bg_cube_model.background[:, det_bin[0], det_bin[1]]
    # TODO: get also energies (x coord) of the points!!!
    print("model data")
    print(model_data)

    # test if both arrays are equal
    assert_allclose(plot_data[:,1], model_data.value)

    # test write (save)
    # test if values are correct in the saved file: compare both files
    bg_model_1 = bg_cube_model
    if not USE_TEMP_FILES:
        outfile = 'bg_model.fits'
    else:
        outfile = NamedTemporaryFile(suffix='.fits').name
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='table', clobber=True) # overwrite
    bg_model_2 = CubeBackgroundModel.read(outfile, format='table')
    assert_allclose(bg_model_2.background, bg_model_1.background)
    assert_allclose(bg_model_2.detx_bins, bg_model_1.detx_bins)
    assert_allclose(bg_model_2.dety_bins, bg_model_1.dety_bins)
    assert_allclose(bg_model_2.energy_bins, bg_model_1.energy_bins)

    # test read/write image file
    if not USE_TEMP_FILES:
        outfile = 'bg_model_image.fits'
    else:
        outfile = NamedTemporaryFile(suffix='.fits').name
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='image', clobber=True) # overwrite
    # test: this function should produce:
    #  - a file exactly as the other method
    #  - a cube exactly as the other method (once the file is read with the read function)

    # test if values are correct in the saved file: compare both files
    bg_model_1 = bg_cube_model
    bg_model_2 = CubeBackgroundModel.read(outfile, format='image')
    assert_allclose(bg_model_2.background, bg_model_1.background)
    assert_allclose(bg_model_2.detx_bins, bg_model_1.detx_bins)
    assert_allclose(bg_model_2.dety_bins, bg_model_1.dety_bins)
    assert_allclose(bg_model_2.energy_bins, bg_model_1.energy_bins)

    # TODO: test cubes/plots with asymmetric shape (x_bins != y_bins) !!!

    # TODO: doc for plots, example plots (revert read/write changes? -> no) !!!
    #       my scripts: plot stack + clean code
    #       review "use_plot_something.py"

    # TODO: clean up after tests (remove created files) !!!!!!!!!!!!!!!!!!!!!! (add option/flag to aventually keep them)

    plt.show() #don't quit at the end


def test_make_test_bg_cube_model(debug=False):
    """
    Testing make_test_bg_cube_model.
    """
    # call the function without arguments
    bg_cube_model = make_test_bg_cube_model()

    # plots (images and spectra)
    if debug:
        #make plots
        CBMutils.plot_images(bg_cube_model)
        CBMutils.plot_spectra(bg_cube_model, format='stack') # slow!

    outfile = 'test_bg_cube_model_table.fits'
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='table', clobber=True) # overwrite

    outfile = 'test_bg_cube_model_image.fits'
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='image', clobber=True) # overwrite

    # make a cube bg model with non-equal axes
    ndetx_bins = 1
    ndety_bins = 2
    nenergy_bins = 3
    bg_cube_model = make_test_bg_cube_model(ndetx_bins=ndetx_bins, ndety_bins=ndety_bins, nenergy_bins=nenergy_bins)

    # plots (images and spectra)
    if debug:
        #make plots
        CBMutils.plot_images(bg_cube_model)
        CBMutils.plot_spectra(bg_cube_model, format='stack') # slow!

    outfile = 'test_bg_cube_model_xydiff_table.fits'
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='table', clobber=True) # overwrite

    outfile = 'test_bg_cube_model_xydiff_image.fits'
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='image', clobber=True) # over

    # test shape of cube bg model
    assert len(bg_cube_model.background.shape) == 3
    assert bg_cube_model.background.shape == (nenergy_bins, ndety_bins, ndetx_bins)

    # make masked bg model
    bg_cube_model = make_test_bg_cube_model(apply_mask=True)

    # plots (images and spectra)
    if debug:
        #make plots
        CBMutils.plot_images(bg_cube_model)
        #CBMutils.plot_spectra(bg_cube_model, format='stack') # slow! #this should fail because of 0 plots in log axis!

    outfile = 'test_bg_cube_model_masked_table.fits'
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='table', clobber=True) # overwrite

    outfile = 'test_bg_cube_model_masked_image.fits'
    print("Writing file {}".format(outfile))
    bg_cube_model.write(outfile, format='image', clobber=True) # overwrite

    # test that values with (x, y) > (0, 0) are zero
    x_points = Angle(np.arange(5), 'degree') + Angle(0.01, 'degree')
    y_points = Angle(np.arange(5), 'degree') + Angle(0.01, 'degree')
    e_points = bg_cube_model.energy_bin_centers
    x_points, y_points, e_points = np.meshgrid(x_points, y_points, e_points,
                                               indexing='ij')
    det_bin_index = bg_cube_model.find_det_bin(Angle([x_points, y_points]))
    e_bin_index = bg_cube_model.find_energy_bin(e_points)
    bg = bg_cube_model.background[e_bin_index, det_bin_index[1], det_bin_index[0]]

    #assert that values are 0
    assert_allclose(bg, 0.)

def test_remote_data():
    """Testing the use of remote data in gammapy.
    """

    # test local path
    # checks (localy) in gammapy/gammapy/datasets/data
    print()
    local_path = datasets.get_path('fermi/fermi_counts.fits.gz')
    print("local_path", local_path)

    # test remote path
    # checks (remotely) in gammapy/gammapy-extra/datasets
    print()
    remote_path = datasets.get_path('vela_region/counts_vela.fits', location='remote', cache=CACHE)
    print("remote_path", remote_path)

    # test local path
    print()
    # checks (localy) in gammapy/gammapy/datasets/data
    #local_path = datasets.get_path('bg_test.fits')
    #local_path = datasets.get_path('data/bg_test.fits')
    local_path = datasets.get_path('../../background/tests/data/bg_test.fits')
    print("local_path", local_path)

    # test remote path
    print()
    # checks (remotely) in gammapy/gammapy-extra/datasets
    #remote_path = datasets.get_path('bg_cube_model_test.fits', location='remote', cache=CACHE)
    remote_path = datasets.get_path('../test_datasets/background/bg_cube_model_test.fits', location='remote', cache=CACHE)
    print("remote_path", remote_path)


if __name__ == '__main__':

    # create a list of files to test
    filenames = []

    ###DIR = '/Users/deil/work/_Data/hess/HESSFITS/pa/Model_Deconvoluted_Prod26/Mpp_Std/background/'
    DIR = '/home/mapaz/astropy/testing_cube_bg_michael_mayer/background/'
    filename = DIR + 'hist_alt3_az0.fits.gz'
    filenames.append(filename)

    #DIR = '/home/mapaz/astropy/development_code/gammapy/gammapy/background/tests/data/'
    #filename = DIR + 'bg_test.fits'
    #filename = DIR + 'bkgcube.fits' # not supported!
    filename = '../test_datasets/background/bg_cube_model_test.fits'
    filename = datasets.get_path(filename, location='remote', cache=CACHE)
    #DIR = '/home/mapaz/astropy/development_code/gammapy-extra/test_datasets/background/'
    #filename = DIR + 'bg_cube_model_test.fits'
    filenames.append(filename)

    for filename in filenames:
        print()
        print("filename: {}".format(filename))

        # call tests
        #cube_bg_model_plots(filename) # takes long! (many plots/files created!)
        #test_cube_bg_model_class(filename)

    # call tests
    test_make_test_bg_cube_model(False)
    #test_make_test_bg_cube_model(True)
    #test_remote_data()