# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.metadata.primitives import *


class Test(unittest.TestCase):

    def testText(self):
        from music21 import metadata

        text = metadata.primitives.Text('my text')
        text.language = 'en'
        self.assertEqual(text._data, 'my text')
        self.assertEqual(text._language, 'en')

    def testContributor(self):
        from music21 import metadata

        contributor = metadata.primitives.Contributor(
            role='composer',
            name='Gilles Binchois',
        )
        self.assertEqual(contributor.role, 'composer')
        self.assertEqual(contributor.relevance, 'contributor')
        self.assertEqual(contributor.name, 'Gilles Binchois')

    def testCreator(self):
        from music21 import metadata

        creator = metadata.primitives.Creator(
            role='composer',
            name='Gilles Binchois',
        )
        self.assertEqual(creator.role, 'composer')
        self.assertEqual(creator.relevance, 'creator')
        self.assertEqual(creator.name, 'Gilles Binchois')

    def testDate(self):
        from music21 import metadata

        date1 = metadata.primitives.Date(year=1843, yearError='approximate')
        date2 = metadata.primitives.Date(year='1843?')

        self.assertEqual(date1.year, 1843)
        self.assertEqual(date1.yearError, 'approximate')

        self.assertEqual(date2.year, 1843)
        self.assertEqual(date2.yearError, 'uncertain')

    def testDateValueError(self):
        with self.assertRaisesRegex(ValueError, 'Month must be.*not 13'):
            Date(month=13)

        for d, m, y in ((32, None, None),
                        (0, None, None),
                        (31, 4, None),
                        (30, 2, None),
                        (29, 2, 1999),
                        ):
            with self.assertRaisesRegex(ValueError, 'Day.*is not possible'):
                Date(year=y, month=m, day=d)

        with self.assertRaisesRegex(ValueError, 'Hour'):
            Date(hour=24)
        with self.assertRaisesRegex(ValueError, 'Minute'):
            Date(minute=61)
        with self.assertRaisesRegex(ValueError, 'Second'):
            Date(second=-1)

        self.assertIsNotNone(Date(year=2000, month=2, day=29))
        self.assertIsNotNone(Date(month=2, day=29))
        self.assertIsNotNone(Date(month=12, day=31))
        self.assertIsNotNone(Date(hour=23, minute=59, second=59))

    def testDateSingle(self):
        from music21 import metadata

        dateSingle = metadata.primitives.DateSingle(
            '2009/12/31', 'approximate')
        self.assertEqual(str(dateSingle), '2009/12/31')
        self.assertEqual(len(dateSingle._data), 1)
        self.assertEqual(dateSingle._relevance, 'approximate')
        self.assertEqual(dateSingle._dataUncertainty, ['approximate'])

    def testDateRelative(self):
        from music21 import metadata

        dateRelative = metadata.primitives.DateRelative('2001/12/31', 'prior')
        self.assertEqual(str(dateRelative), 'prior to 2001/12/31')
        self.assertEqual(dateRelative.relevance, 'prior')
        self.assertEqual(len(dateRelative._data), 1)
        self.assertEqual(dateRelative._dataUncertainty, [None])

    def testDateBetween(self):
        from music21 import metadata

        dateBetween = metadata.primitives.DateBetween(
            ('2009/12/31', '2010/1/28'))
        self.assertEqual(str(dateBetween), '2009/12/31 to 2010/01/28')
        self.assertEqual(dateBetween.relevance, 'between')
        self.assertEqual(dateBetween._dataUncertainty, [None, None])
        self.assertEqual(len(dateBetween._data), 2)

    def testDateSelection(self):
        from music21 import metadata

        dateSelection = metadata.primitives.DateSelection(
            ['2009/12/31', '2010/1/28', '1894/1/28'],
            'or',
        )
        self.assertEqual(str(dateSelection),
                         '2009/12/31 or 2010/01/28 or 1894/01/28')
        self.assertEqual(dateSelection.relevance, 'or')
        self.assertEqual(dateSelection._dataUncertainty, [None, None, None])
        self.assertEqual(len(dateSelection._data), 3)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
