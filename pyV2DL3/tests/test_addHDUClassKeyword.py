from astropy.table import Table, vstack
from astropy.io import fits
import numpy as np
import pyV2DL3.addHDUClassKeyword

def test_addHDUClassKeyword():

   n = np.arange(100.0)
   hdu = fits.PrimaryHDU(n)
   hdu=pyV2DL3.addHDUClassKeyword.addHDUClassKeyword(hdu,
                          'INDEX',
                          'OBS')
   hdu.verify('warn')

if __name__ == '__main__':
   test_addHDUClassKeyword()
