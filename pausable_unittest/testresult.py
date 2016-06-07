# -*- coding: utf-8 -*-

import sys
import traceback
import logging
import picklablelogger

__unittest = False

class TestResult(object):
    def __init__(self, stream_type="stdout", filename=None, loglevel=logging.DEBUG):
        self.shouldStop = False
        self.failFast = False
        self.pausable_runner = None

        self.logger = logging.getLogger("pasable_unittest")
        self.logger.setLevel(loglevel)
        self.logger.addHandler(picklablelogger.PicklableStreamHandler(stream_type))
        if filename != False:
            self.logger.addHandler(picklablelogger.PicklableFileHandler(filename))

        self._stream_type = stream_type
        self._results = []
        self._file = None
        self._running_test = None

    def before_pause(self, info):
        self.raw_log("Pause...")

        for handler in self.logger.handlers:
            if hasattr(handler, "prepare_for_pause"):
                handler.prepare_for_pause()

    def after_pause(self, info):
        for handler in self.logger.handlers:
            if hasattr(handler, "resume_from_pause"):
                handler.resume_from_pause()

        self.raw_log("Resume...")

        self._writeln("-" * 70)
        if len(self._results) > 0:
            self._writeln("Current results:")
            for result in self._results:
                self.show_result(result)
            self._writeln("-" * 70)
            self._writeln("")
        if self._running_test:
            self._writeln(self._running_test + " is running.")


    def _filterResult(self, type):
        return [ (x[1], x[2]) for x in self._results if x[0] == type ]

    def show_result(self, result):
        result_type = result[0]
        if result_type in { "success", "expected_failure", "skip" }:
            ok = True
        else:
            ok = False
        self._writeln(result_type.ljust(7, " ") + ": " + str(result[1]))
        if not ok:
            self._writeln(self._exc_info_to_string(result[2], result[1]))

    def show_results(self):
        self._writeln("")
        self._writeln("=" * 70)
        self._writeln("Results:")
        for result in self._results:
            self.show_result(result)
        self._writeln("=" * 70)

    @property
    def errors(self):
        return self._filterResult("error")

    @property
    def failures(self):
        return self._filterResult("failure")

    @property
    def skipped(self):
        return self._filterResult("skip")

    @property
    def expectedFailures(self):
        return self._filterResult("expected_failure")

    @property
    def unexpectedSuccesses(self):
        return self._filterResult("unexpected_successes")

    @property
    def successes(self):
        return self._filterResult("success")

    @property
    def testsRun(self):
        return len(self._results)

    def stop(self):
        self.shouldStop = True


    def _outputResult(self):
        pass

    def addResult(self, type, test, err=None):
        self._results.append((type, test, err))

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def _output_stream(self):
        if self._stream_type == "stdout":
            return sys.stdout
        elif self._stream_type == "stderr":
            return sys.stderr
        else:
            raise "Invalid _stream_type"

    def raw_log(self, text):
        for handler in self.logger.handlers:
            if hasattr(handler, "raw_writeln"):
                handler.raw_writeln(text)

    def _writeln(self, str):
        output = self._output_stream()
        output.write(str + "\n")

    def startTest(self, test):
        desc = self.getDescription(test)
        self._running_test = desc
        self.logger.info(desc)

    def stopTest(self, test):
        pass

    def startTestRun(self, test):
        pass

    def stopTestRun(self, test):
        pass

    def addSuccess(self, test):
        self.addResult("success", test)
        self.raw_log(self._running_test + " => ok")

    def addError(self, test, err):
        self.addResult("error", test, err)
        self.raw_log(self._running_test + " => ERROR")
        self.raw_log(self._exc_info_to_string(err, test))

    def addFailure(self, test, err):
        self.addResult("failure", test, err)
        self.raw_log(self._running_test + " => FAIL")

    def addSkip(self, test, reason):
        self.addResult("skip", test, reason)
        self.raw_log(self._running_test + " => skipped {0!r}".format(reason))

    def addExpectedFailure(self, test, err):
        self.addResult("expected_failure", test, err)
        self.raw_log(self._running_test + " => expected failure")

    def addUnexpectedSuccess(self, test):
        self.addResult("unexpected_success", test)
        self.raw_log(self._running_test + " => unexpected success")

    def _is_relevant_tb_level(self, tb):
        return '__unittest' in tb.tb_frame.f_globals

    def _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = traceback.format_exception(exctype, value, tb, length)
        else:
            msgLines = traceback.format_exception(exctype, value, tb)

        return ''.join(msgLines)

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

