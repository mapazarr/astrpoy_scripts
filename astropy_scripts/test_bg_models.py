from __future__ import (absolute_import, division, print_function,
                        unicode_literals) # python 2 as python 3
import numpy as np
import matplotlib.pyplot as plt
from astropy.units import Quantity
from astropy.coordinates import Angle
from gammapy.background.models import CubeBackgroundModel

GRAPH_DEBUG = 0

def plot_example():
    """Plot background model and store as cube so that it can viewed with ds9.
    """
    #DIR = '/Users/deil/work/_Data/hess/HESSFITS/pa/Model_Deconvoluted_Prod26/Mpp_Std/background/'
    #DIR = '/home/mapaz/astropy/testing_cube_bg_michael_mayer/background/'
    #filename = DIR + 'hist_alt3_az0.fits.gz'
    DIR = '/home/mapaz/astropy/development_code/gammapy/gammapy/background/tests/data/'
    filename = DIR + 'bg_test.fits'
    bg_model = CubeBackgroundModel.read(filename)

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

    bg_model.write_cube('cube_background_model.fits')

def gammapy_tests():
    """Testing the tests for gammapy.
    """
    # test shape of bg cube when reading a file
    #DIR = '/home/mapaz/astropy/development_code/gammapy/gammapy/background/tests/data/'
    ##filenames = ['bg_test.fits', 'bkgcube.fits']
    #filenames = ['bg_test.fits']
    DIR = '/home/mapaz/astropy/testing_cube_bg_michael_mayer/background/'
    filenames = ['hist_alt3_az0.fits.gz']
    # TODO: intentar hacerlo con las IRFs de CTA: !!!!!!!
    # https://github.com/gammapy/gammapy/issues/267
    for filename in filenames:
        print()
        print("filename: {}".format(filename))
        filename = DIR + filename
        bg_cube_model = CubeBackgroundModel.read(filename)
        print("bg_cube_model.background.shape", bg_cube_model.background.shape)
        print("len(bg_cube_model.background.shape)", len(bg_cube_model.background.shape))
        assert len(bg_cube_model.background.shape) == 3
        #import IPython; IPython.embed()

    # test image plot:
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
    decimal = 4
    np.testing.assert_almost_equal(plot_data, model_data.value, decimal)


    # test spectrum plot:
    # test bg rate values plotted for spectrum plot of detector bin conaining det (0, 0) deg (center)
    det = Angle([0., 0.], 'degree')
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
    decimal = 4
    np.testing.assert_almost_equal(plot_data[:,1], model_data.value, decimal)


    plt.show()#TODO: use graph debug!!!! (or not?)

    #TODO: creo que el archivo de ejemplo tiene detx dety en radianes!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!(y yo con las unidades hardcoded :-D)!!!!
    # mirar si ese archivo tiene las unidades por algun sitio....!!!!!!!!!!!!!!!!!!!

    #TODO: test save!!!!


if __name__ == '__main__':
    #plot_example()
    gammapy_tests()
