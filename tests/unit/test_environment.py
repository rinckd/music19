# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.environment import *


class Test(unittest.TestCase):
    import stat

    def stringFromTree(self, settingsTree):
        etIndent(settingsTree.getroot())
        bio = io.BytesIO()
        settingsTree.write(bio, encoding='utf-8', xml_declaration=True)
        match = bio.getvalue().decode('utf-8')
        return match

    @unittest.skipIf(common.getPlatform() == 'win', 'test assumes Unix-style paths')


    @unittest.skipIf(common.getPlatform() == 'win', 'test assumes Unix-style paths')
    def testEnvironmentA(self):
        env = Environment(forcePlatform='darwin')

        # No path: https://github.com/cuthbertLab/music21/issues/551
        self.assertIsNone(env['localCorpusPath'])

        # setting the local corpus path pref is like adding a path
        env['localCorpusPath'] = '/a'
        self.assertEqual(list(env['localCorpusSettings']), ['/a'])

        env['localCorpusPath'] = '/b'
        self.assertEqual(list(env['localCorpusSettings']), ['/a', '/b'])

    @unittest.skipUnless(
        common.getPlatform() in ['nix', 'darwin'],
        'os.getuid can be called only on Unix platforms'
    )
    def testGetDefaultRootTempDir(self):
        import stat

        e = Environment()
        oldScratchDir = e['directoryScratch']
        oldTempDir = None
        oldPermission = None
        newTempDir = None
        try:
            e['directoryScratch'] = None
            oldTempDir = e.getDefaultRootTempDir()
            oldPermission = oldTempDir.stat()[stat.ST_MODE]
            # Wipe out write, exec permissions on the default root dir
            os.chmod(oldTempDir, stat.S_IREAD)
            newTempDir = e.getDefaultRootTempDir()
            self.assertIn(f'music21-userid-{os.getuid()}', str(newTempDir))
        finally:
            # Make sure oldTempDir and oldPermission is set in 'try' block
            if oldTempDir is not None and oldPermission is not None:
                # Restore original permissions and original path
                os.chmod(oldTempDir, oldPermission)
                e['directoryScratch'] = oldScratchDir

            # Make sure newTempDir is set in 'try' block
            if newTempDir is not None:
                # If getting OSError while trying to create the directory on the first fallback,
                # the default temp directory from tempfile.gettempdir() will be return on the second
                # fallback. We don't want to delete the default temp directory. Therefore we check
                # it before deleting.
                #
                # For security concerns, we are not sure that newTempDir is always a directory
                # which can be removed safely. For example, if newTempDir is "/" for unknown reason,
                # remove newTempDir could potentially destroy an entire hard drive. To avoid this
                # situation, we check newTempDir first, making sure that newTempDir is an empty
                # directory which means (1) it's a directory we create in this test or (2) we won't
                # destroy anything if we delete it, and then delete it with os.rmdir, which could
                # only delete an empty directory. We don't set an exception-catching block here
                # because we have checked this directory is empty.
                tmp = newTempDir.samefile(tempfile.gettempdir())
                empty = len(os.listdir(newTempDir)) == 0
                if not tmp and empty:
                    os.rmdir(newTempDir)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
