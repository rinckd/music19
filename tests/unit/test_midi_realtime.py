# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.midi.realtime import *


class Test(unittest.TestCase):
    pass


class TestExternal(unittest.TestCase):  # pragma: no cover
    loader = find_spec('pygame')
    if loader is not None:  # pragma: no cover
        pygame_installed = True
    else:
        pygame_installed = False

    @unittest.skipUnless(pygame_installed, 'pygame is not installed')
    def testBachDetune(self):
        from music21 import corpus
        import random
        b = corpus.parse('bwv66.6')
        keyDetune = []
        for i in range(127):
            keyDetune.append(random.randint(-30, 30))
        for n in b.recurse().notes:
            n.pitch.microtone = keyDetune[n.pitch.midi]
        sp = StreamPlayer(b)
        sp.play()

        # # testing playForMilliseconds
        # sp.play(playForMilliseconds=2000)

        # # testing blocked=False
        # sp.play(blocked=False)
        # import time
        # time.sleep(2)
        # sp.stop()
        # time.sleep(1)

    def x_testBusyCallback(self):
        '''
        tests to see if the busyCallback function is called properly
        '''

        from music21 import corpus
        import random

        def busyCounter(timeList):
            timeCounter_inner = timeList[0]
            timeCounter_inner.times += timeCounter_inner.updateTime
            print(f'hi! waited {timeCounter_inner.times} milliseconds')

        class Mock:
            times = 0

        timeCounter = Mock()
        timeCounter.updateTime = 500  # pylint: disable=attribute-defined-outside-init

        b = corpus.parse('bach/bwv66.6')
        keyDetune = []
        for i in range(127):
            keyDetune.append(random.randint(-30, 30))
        for n in b.recurse().notes:
            n.pitch.microtone = keyDetune[n.pitch.midi]
        sp = StreamPlayer(b)
        sp.play(busyFunction=busyCounter, busyArgs=[timeCounter], busyWaitMilliseconds=500)

    def x_testPlayOneMeasureAtATime(self):
        from music21 import corpus
        defaults.ticksAtStart = 0
        b = corpus.parse('bwv66.6')
        measures = []  # store for later
        maxMeasure = len(b.parts[0].getElementsByClass(stream.Measure))
        for i in range(maxMeasure):
            measures.append(b.measure(i))
        sp = StreamPlayer(b)

        for measure in measures:
            sp.streamIn = measure
            sp.play()

    def x_testPlayRealTime(self):
        '''
        doesn't work -- no matter what there's always at least a small lag, even with queues
        '''
        # pylint: disable=attribute-defined-outside-init
        from music21 import note
        import random

        def getRandomStream():
            s = stream.Stream()
            for i in range(4):
                n = note.Note()
                n.ps = random.randint(48, 72)
                s.append(n)
            lastN = note.Note()
            # lastN.duration.quarterLength = 0.75
            s.append(lastN)
            return s

        # noinspection PyShadowingNames
        def restoreList(timeList):
            timeCounter = timeList[0]
            streamPlayer = timeList[1]
            currentPos = streamPlayer.pygame.mixer.music.get_pos()
            if currentPos < 500 <= timeCounter.lastPos:
                timeCounter.times -= 1
                if timeCounter.times > 0:
                    streamPlayer.streamIn = getRandomStream()
                    # timeCounter.oldIOFile = timeCounter.storedIOFile
                    timeCounter.storedIOFile = streamPlayer.getStringOrBytesIOFile()
                    streamPlayer.pygame.mixer.music.queue(timeCounter.storedIOFile)
                    timeCounter.lastPos = currentPos
            else:
                timeCounter.lastPos = currentPos

        class TimePlayer:
            ready = False
            times = 3
            lastPos = 1000

        timeCounter = TimePlayer()

        b = getRandomStream()
        sp = StreamPlayer(b)
        timeCounter.storedIOFile = sp.getStringOrBytesIOFile()
        while timeCounter.times > 0:
            timeCounter.ready = False
            sp.playStringIOFile(timeCounter.storedIOFile,
                                busyFunction=restoreList,
                                busyArgs=[timeCounter, sp],
                                busyWaitMilliseconds=30)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
