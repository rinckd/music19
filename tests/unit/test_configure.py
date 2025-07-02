# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.configure import *


class Test(unittest.TestCase):

    def testYesOrNo(self):
        from music21 import configure
        d = configure.YesOrNo(default=True, tryAgain=False,
                              promptHeader='Are you ready to continue?')
        d.askUser('n')
        self.assertEqual(str(d.getResult()), 'False')
        d.askUser('y')
        self.assertEqual(str(d.getResult()), 'True')
        d.askUser('')  # gets default
        self.assertEqual(str(d.getResult()), 'True')
        d.askUser('blah')  # gets default
        self.assertEqual(str(d.getResult()), '<music21.configure.IncompleteInput: blah>')

        d = configure.YesOrNo(default=None, tryAgain=False,
                              promptHeader='Are you ready to continue?')
        d.askUser('n')
        self.assertEqual(str(d.getResult()), 'False')
        d.askUser('y')
        self.assertEqual(str(d.getResult()), 'True')
        d.askUser('')  # gets default
        self.assertEqual(str(d.getResult()), '<music21.configure.NoInput: None>')
        d.askUser('blah')  # gets default
        self.assertEqual(str(d.getResult()), '<music21.configure.IncompleteInput: blah>')

    def testSelectFromList(self):
        from music21 import configure
        d = configure.SelectFromList(default=1)
        self.assertEqual(d._default, 1)

    def testSelectMusicXMLReaders(self):
        from music21 import configure
        d = configure.SelectMusicXMLReader()
        # force request to user by returning no valid results

        def getValidResults(force=None):
            return []

        d._getValidResults = getValidResults
        d.askUser(force='n', skipIntro=True)  # reject option to open in a browser
        post = d.getResult()
        # returns a bad condition b/c there are no options and user entered 'n'
        self.assertIsInstance(post, configure.BadConditions)

    def testRe(self):
        g = reFinaleApp.search('Finale 2011.app')
        self.assertEqual(g.group(0), 'Finale 2011.app')

        self.assertEqual(reFinaleApp.search('final blah 2011'), None)

        g = reFinaleApp.search('Finale.app')
        self.assertEqual(g.group(0), 'Finale.app')

        self.assertEqual(reFinaleApp.search('Final Cut 2017.app'), None)

    def testConfigurationAssistant(self):
        unused_ca = ConfigurationAssistant(simulate=True)

    def testGetUserData(self):
        unused_d = AskSendInstallationReport()
        # d.askUser()
        # d.getResult()
        # d.performAction()

    def testGetUserData2(self):
        unused_d = AskAutoDownload()
        # d.askUser()
        # d.getResult()
        # d.performAction()

    def testAnyKey(self):
        unused_d = AnyKey()
        # d.askUser()
        # d.getResult()
        # d.performAction()


class TestUserInput(unittest.TestCase):  # pragma: no cover

    def testYesOrNo(self):
        print()
        print('starting: YesOrNo()')
        d = YesOrNo()
        d.askUser()
        print('getResult():', d.getResult())

        print()
        print('starting: YesOrNo(default=True)')
        d = YesOrNo(default=True)
        d.askUser()
        print('getResult():', d.getResult())

        print()
        print('starting: YesOrNo(default=False)')
        d = YesOrNo(default=False)
        d.askUser()
        print('getResult():', d.getResult())

    def testSelectMusicXMLReader(self):
        print()
        print('starting: SelectMusicXMLReader()')
        d = SelectMusicXMLReader()
        d.askUser()
        print('getResult():', d.getResult())

    def testSelectMusicXMLReaderDefault(self):
        print()
        print('starting: SelectMusicXMLReader(default=1)')
        d = SelectMusicXMLReader(default=1)
        d.askUser()
        print('getResult():', d.getResult())

    def testOpenInBrowser(self):
        print()
        d = AskOpenInBrowser('https://www.music21.org/')
        d.askUser()
        print('getResult():', d.getResult())
        d.performAction()

    def testSelectMusicXMLReader2(self):
        print()
        print('starting: SelectMusicXMLReader()')
        d = SelectMusicXMLReader()
        d.askUser()
        print('getResult():', d.getResult())
        d.performAction()

        print()
        print('starting: SelectMusicXMLReader() w/o results')
        d = SelectMusicXMLReader()
        # force request to user by returning no valid results

        def getValidResults(force=None):
            return []

        d._getValidResults = getValidResults
        d.askUser()
        print('getResult():', d.getResult())
        d.performAction()

    def testConfigurationAssistant(self):
        print('Running ConfigurationAssistant all')
        configAsst = ConfigurationAssistant(simulate=True)
        configAsst.run()


def run():
    ca = ConfigurationAssistant()
    ca.run()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
