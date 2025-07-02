# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.graph.primitives import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())


class TestExternal(unittest.TestCase):
    show = True

    def testBasic(self):
        a = GraphScatter(doneAction=None, title='x to x*x', alpha=1)
        data = [(x, x * x) for x in range(50)]
        a.data = data
        a.process()

        a = GraphHistogram(doneAction=None, title='50 x with random(30) y counts')
        data = [(x, random.choice(range(30))) for x in range(50)]
        a.data = data
        a.process()

        a = Graph3DBars(doneAction=None,
                               title='50 x with random values increase by 10 per x',
                               alpha=0.8,
                               colors=['b', 'g'])
        data = []
        for i in range(1, 4):
            q = [(x, random.choice(range(10 * i, 10 * (i + 1))), i) for x in range(50)]
            data.extend(q)
        a.data = data
        a.process()

        del a

    def testBrokenHorizontal(self):
        data = []
        for label in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
            points = []
            for i in range(10):
                start = random.choice(range(150))
                end = start + random.choice(range(50))
                points.append((start, end))
            data.append([label, points])

        a = GraphHorizontalBar(doneAction=None)
        a.data = data
        a.process()

    def testScatterWeighted(self):
        data = []
        for i in range(50):
            x = random.choice(range(20))
            y = random.choice(range(20))
            z = random.choice(range(1, 20))
            data.append([x, y, z])

        if self.show:
            doneAction = 'write'
        else:
            doneAction = None
        a = GraphScatterWeighted(doneAction=doneAction)
        a.data = data
        a.process()

    def x_test_writeAllGraphs(self):
        '''
        Write a graphic file for all graphs,
        naming them after the appropriate class.
        This is used to generate documentation samples.
        '''

        # get some data
        data3DPolygonBars = []
        for i in range(1, 4):
            q = [(x, random.choice(range(10 * (i + 1))), i) for x in range(20)]
            data3DPolygonBars.extend(q)

        # pair data with class name
        # noinspection SpellCheckingInspection
        graphClasses = [
            (GraphHorizontalBar,
             [('Chopin', [(1810, 1849 - 1810)]),
              ('Schumanns', [(1810, 1856 - 1810), (1819, 1896 - 1819)]),
              ('Brahms', [(1833, 1897 - 1833)])]
             ),
            (GraphScatterWeighted,
             [(23, 15, 234), (10, 23, 12), (4, 23, 5), (15, 18, 120)]),
            (GraphScatter,
             [(x, x * x) for x in range(50)]),
            (GraphHistogram,
             [(x, random.choice(range(30))) for x in range(50)]),
            (Graph3DBars, data3DPolygonBars),
            (GraphColorGridLegend,
             [('Major', [('C', '#00AA55'), ('D', '#5600FF'), ('G', '#2B00FF')]),
              ('Minor', [('C', '#004600'), ('D', '#00009b'), ('G', '#00009B')]), ]
             ),
            (GraphColorGrid, [['#8968CD', '#96CDCD', '#CD4F39'],
                              ['#FFD600', '#FF5600'],
                              ['#201a2b', '#8f73bf', '#a080d5', '#6495ED', '#FF83FA'],
                              ]
             ),

        ]

        for graphClassName, data in graphClasses:
            obj = graphClassName(doneAction=None)
            obj.data = data  # add data here
            obj.process()
            fn = obj.__class__.__name__ + '.png'
            fp = str(environLocal.getRootTempDir() / fn)
            environLocal.printDebug(['writing fp:', fp])
            obj.write(fp)

    def x_test_writeGraphColorGrid(self):
        # this is temporary
        a = GraphColorGrid(doneAction=None)
        data = [['#525252', '#5f5f5f', '#797979', '#858585', '#727272', '#6c6c6c',
                 '#8c8c8c', '#8c8c8c', '#6c6c6c', '#999999', '#999999', '#797979',
                 '#6c6c6c', '#5f5f5f', '#525252', '#464646', '#3f3f3f', '#3f3f3f',
                 '#4c4c4c', '#4c4c4c', '#797979', '#797979', '#4c4c4c', '#4c4c4c',
                 '#525252', '#5f5f5f', '#797979', '#858585', '#727272', '#6c6c6c'],
                ['#999999', '#999999', '#999999', '#999999', '#999999', '#999999',
                 '#999999', '#999999', '#999999', '#999999', '#999999', '#797979',
                 '#6c6c6c', '#5f5f5f', '#5f5f5f', '#858585', '#797979', '#797979',
                 '#797979', '#797979', '#797979', '#797979', '#858585', '#929292', '#999999'],
                ['#999999', '#999999', '#999999', '#999999', '#999999', '#999999',
                 '#999999', '#999999', '#999999', '#999999', '#999999', '#999999',
                 '#8c8c8c', '#8c8c8c', '#8c8c8c', '#858585', '#797979', '#858585',
                 '#929292', '#999999'],
                ['#999999', '#999999', '#999999', '#999999', '#999999', '#999999',
                 '#999999', '#999999', '#999999', '#999999', '#999999', '#999999',
                 '#8c8c8c', '#929292', '#999999'],
                ['#999999', '#999999', '#999999', '#999999', '#999999', '#999999',
                 '#999999', '#999999', '#999999', '#999999'],
                ['#999999', '#999999', '#999999', '#999999', '#999999']]
        a.data = data
        a.process()
        fn = a.__class__.__name__ + '.png'
        fp = str(environLocal.getRootTempDir() / fn)

        a.write(fp)

    def x_test_writeGraphingDocs(self):
        '''
        Write graphing examples for the docs
        '''
        post = []

        a = GraphScatter(doneAction=None)
        data = [(x, x * x) for x in range(50)]
        a.data = data
        post.append([a, 'graphing-01'])

        a = GraphScatter(title='Exponential Graph', alpha=1, doneAction=None)
        data = [(x, x * x) for x in range(50)]
        a.data = data
        post.append([a, 'graphing-02'])

        a = GraphHistogram(doneAction=None)
        data = [(x, random.choice(range(30))) for x in range(50)]
        a.data = data
        post.append([a, 'graphing-03'])

        a = Graph3DBars(doneAction=None)
        data = []
        for i in range(1, 4):
            q = [(x, random.choice(range(10 * (i + 1))), i) for x in range(20)]
            data.extend(q)
        a.data = data
        post.append([a, 'graphing-04'])

        b = Graph3DBars(title='Random Data',
                        alpha=0.8,
                        barWidth=0.2,
                        doneAction=None,
                        colors=['b', 'r', 'g'])
        b.data = data
        post.append([b, 'graphing-05'])

        for obj, name in post:
            obj.process()
            fn = name + '.png'
            fp = str(environLocal.getRootTempDir() / fn)
            environLocal.printDebug(['writing fp:', fp])
            obj.write(fp)

    def testColorGridLegend(self, doneAction=None):
        from music21.analysis import discrete

        ks = discrete.KrumhanslSchmuckler()
        data = ks.solutionLegend()
        # print(data)
        a = GraphColorGridLegend(doneAction=doneAction, dpi=300)
        a.data = data
        a.process()

    def testGraphVerticalBar(self):
        g = GraphGroupedVerticalBar(doneAction=None)
        data = [(f'bar{x}', {'a': 3, 'b': 2, 'c': 1}) for x in range(10)]
        g.data = data
        g.process()

    def testGraphNetworkxGraph(self):
        extm = getExtendedModules()

        if extm.networkx is not None:  # pragma: no cover
            b = GraphNetworkxGraph(doneAction=None)
            # b = GraphNetworkxGraph()
            b.process()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
