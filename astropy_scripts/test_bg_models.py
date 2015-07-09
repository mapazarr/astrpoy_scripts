from __future__ import (absolute_import, division, print_function,
                        unicode_literals) # python 2 as python 3
from tempfile import NamedTemporaryFile
import numpy as np
from numpy.testing import assert_allclose
import matplotlib.pyplot as plt
from astropy.units import Quantity
from astropy.coordinates import Angle
from gammapy.background import CubeBackgroundModel
from gammapy.background import make_linear_bin_edges_arrays_from_wcs, make_linear_wcs_from_bin_edges_arrays
from gammapy import datasets

GRAPH_DEBUG = 0
USE_TEMP_FILES = 0

def plot_example():
    """Plot background model and store as cube so that it can viewed with ds9.
    """
    ###DIR = '/Users/deil/work/_Data/hess/HESSFITS/pa/Model_Deconvoluted_Prod26/Mpp_Std/background/'
    ##DIR = '/home/mapaz/astropy/testing_cube_bg_michael_mayer/background/'
    ##filename = DIR + 'hist_alt3_az0.fits.gz'
    #DIR = '/home/mapaz/astropy/development_code/gammapy/gammapy/background/tests/data/'
    #filename = DIR + 'bg_test.fits'
    filename = '../test_datasets/background/bg_cube_model_test.fits'
    filename = datasets.get_path(filename, location='remote')

    bg_model = CubeBackgroundModel.read_bin_table(filename)

    bg_model.plot_images()
    #bg_model.plot_images(energy=Quantity(1., 'TeV'))
    bg_model.plot_images(energy=Quantity(2., 'TeV'))
    #bg_model.plot_images(energy=Quantity(3., 'TeV'))
    #bg_model.plot_images(energy=Quantity(1.53216636, 'TeV'))
    #bg_model.plot_images(energy=Quantity(2.27553916, 'TeV'))
    #bg_model.plot_images(energy=Quantity(80., 'TeV'))
    #bg_model.plot_images(energy=Quantity([1.], 'TeV'))
    #bg_model.plot_images(energy=Quantity([2.], 'TeV'))
    #bg_model.plot_images(energy=Quantity([1., 2.], 'TeV'))

    bg_model.plot_spectra()
    bg_model.plot_spectra(det=Angle([0., 0.], 'degree'))
    #bg_model.plot_spectra(det=Angle([0., 2.], 'degree'))
    #bg_model.plot_spectra(det=Angle([-5., 0.], 'degree'))
    #bg_model.plot_spectra(det=Angle([0., -5.], 'degree'))
    #bg_model.plot_spectra(det=Angle([-5., -5.], 'degree'))
    #bg_model.plot_spectra(det=Angle([[0., 0.]], 'degree'))
    #bg_model.plot_spectra(det=Angle([[0., 0.], [1., 1.]], 'degree'))

    outfile = 'cube_background_model.fits'
    bg_model.write_image(outfile, clobber=True) # overwrite


def gammapy_tests():
    """Testing the tests for gammapy.
    """
    # test shape of bg cube when reading a file
    #DIR = '/home/mapaz/astropy/development_code/gammapy/gammapy/background/tests/data/'
    ##filenames = ['bg_test.fits', 'bkgcube.fits']
    ## WARNING! bkgcube.fits has a different format:
    ## I think it's projected bg model in RA dec!!!
    ## (maybe we need an extra class for this?!!!)
    #filenames = ['bg_test.fits']
    ##DIR = '/home/mapaz/astropy/testing_cube_bg_michael_mayer/background/'
    ##filenames = ['hist_alt3_az0.fits.gz']
    ## TODO: intentar hacerlo con las IRFs de CTA: !!!!!!!
    ## https://github.com/gammapy/gammapy/issues/267
    filenames = ['../test_datasets/background/bg_cube_model_test.fits']
    for filename in filenames:
        print()
        print("filename: {}".format(filename))
        #filename = DIR + filename
        filename = datasets.get_path(filename, location='remote')
        bg_cube_model = CubeBackgroundModel.read_bin_table(filename)
        print("bg_cube_model.background.shape", bg_cube_model.background.shape)
        print("len(bg_cube_model.background.shape)", len(bg_cube_model.background.shape))
        assert len(bg_cube_model.background.shape) == 3
        #import IPython; IPython.embed()

    # test image plot: (OLD BORRAR!!!!)
    # test bg rate values plotted for image plot of energy bin conaining E = 2 TeV
    energy = Quantity(2., 'TeV')
    fig_image, ax_im, image_im = bg_cube_model.plot_images(energy)
    plt.draw()
    if GRAPH_DEBUG:
        plt.show() # wait until image is closed
    plot_data = image_im.get_array()
    # I need also the bin ids!!!
    plot_shape = image_im.get_array().shape
    plot_extent = image_im.get_extent()
    print("plot data")
    print(plot_data)
    print("plot shape", plot_shape)
    print("plot extent", plot_extent)

    # get data from bg model object to compare
    energy_bin, energy_bin_edges = bg_cube_model.find_energy_bin(energy)
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
    fig_spec, ax_spec, image_spec = bg_cube_model.plot_spectra(det)
    plt.draw()
    if GRAPH_DEBUG:
        plt.show() # wait until image is closed
    plot_data = ax_spec.get_lines()[0].get_xydata()
    print("plot data")
    print(plot_data)

    # get data from bg model object to compare
    det_bin, det_bin_edges = bg_cube_model.find_det_bin(det)
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
    bg_cube_model.write_bin_table(outfile, clobber=True) # overwrite
    bg_model_2 = CubeBackgroundModel.read_bin_table(outfile)
    assert_allclose(bg_model_2.background.value,
                                   bg_model_1.background.value)
    assert_allclose(bg_model_2.detx_bins.value,
                                   bg_model_1.detx_bins.value)
    assert_allclose(bg_model_2.dety_bins.value,
                                   bg_model_1.dety_bins.value)
    assert_allclose(bg_model_2.energy_bins.value,
                                   bg_model_1.energy_bins.value)

    # test WCS object
    print()
    print("Testing make WCS")
    bins_x = Angle([1., 2., 3., 4.], 'degree')
    #bins_y = Angle([-1.5, 0., 1.5], 'radian')
    bins_y = Angle([-1.5, 0., 1.5], 'degree')
    wcs = make_linear_wcs_from_bin_edges_arrays("X", "Y", bins_x, bins_y)
    wcs_header = wcs.to_header()
    print(repr(wcs_header))
    print()
    print("Testing recover bins")
    nbins_x = len(bins_x) - 1
    nbins_y = len(bins_y) - 1
    reco_bins_x, reco_bins_y = make_linear_bin_edges_arrays_from_wcs(wcs,
                                                                     nbins_x,
                                                                     nbins_y)
    print(repr(reco_bins_x))
    print(repr(reco_bins_y))
    # to deeply test the translation of the bin reconstruction, use this in the wcs creation function:
    #w.wcs.crpix = [10, 15] # smthg different from origin (0.5, 0.5) !!!
    # test: reconstructed bins should match original bins
    assert_allclose(reco_bins_x, bins_x)
    assert_allclose(reco_bins_y, bins_y)

    # TODO: test also read_image and write_image
    outfile = 'bg_model_image.fits'
    bg_cube_model.write_image(outfile, clobber=True) # overwrite


    # TODO: clean up after tests (remove created files) !!!!!!!!!!!!!!!!!!!!!! (add option/flag to aventually keep them)

    plt.show() #don't quit at the end


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
    remote_path = datasets.get_path('vela_region/counts_vela.fits', location='remote')
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
    #remote_path = datasets.get_path('bg_cube_model_test.fits', location='remote')
    remote_path = datasets.get_path('../test_datasets/background/bg_cube_model_test.fits', location='remote')
    print("remote_path", remote_path)


if __name__ == '__main__':
    #plot_example()
    gammapy_tests()
    #test_remote_data()
