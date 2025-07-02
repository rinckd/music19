# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.converter.museScore import *


class Test(unittest.TestCase):
    def pngNumbering(self):
        '''
        Testing findNumberedPNGPath() with files of lengths
        that create .png files with -1, -01, -001, and -0001 in the fp
        '''
        env = environment.Environment()
        for ext_base in '1', '01', '001', '0001':
            png_ext = '-' + ext_base + '.png'

            tmp = env.getTempFile(suffix='.png', returnPathlib=False)
            tmpNumbered = tmp.replace('.png', png_ext)
            os.rename(tmp, tmpNumbered)
            pngFp1 = findNumberedPNGPath(tmp)
            self.assertEqual(str(pngFp1), tmpNumbered)
            os.remove(tmpNumbered)

        # Now with a very long path.
        tmp = env.getTempFile(suffix='.png', returnPathlib=False)
        tmpNumbered = tmp.replace('.png', '-0000001.png')
        os.rename(tmp, tmpNumbered)
        with self.assertRaises(IOError):
            findNumberedPNGPath(tmpNumbered)
        os.remove(tmpNumbered)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
