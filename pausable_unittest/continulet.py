# -*- coding: utf-8 -*-
u"""This file defines a class similar to continulet in PyPy.

Note that this file does not provide complete emulation of continulet
in PyPy, but it is good enough for this library.
"""

import stackless


class _ContinuletInterface(object):
    u"""Continulet-like class, used in tasklet.
    """
    def __init__(self, channel):
        self._channel = channel

    def switch(self, data=None):
        self._channel.send(data)
        return self._channel.receive()


def _tasklet_func(func, channel, *args, **kwargs):
    # Wait for the first switch.
    channel.receive()

    con = _ContinuletInterface(channel)
    value = func(con, *args, **kwargs)
    channel.send(value)


class continulet(object):
    def __init__(self, func, *args, **kwargs):
        self._channel = stackless.channel()
        self._tasklet = stackless.tasklet(_tasklet_func)(func, self._channel,
                                                         *args, **kwargs)
        stackless.run()

    def switch(self, data=None):
        if not self._tasklet.scheduled:
            self._tasklet.insert()
            stackless.run()

        self._channel.send(data)
        return self._channel.receive()

    def restorable(self):
        return self._tasklet.restorable
