# -*- coding: utf-8 -*-

import sys
import traceback
import logging
import time
from . import picklablelogger


class TestResult(object):
    def __init__(self,
                 stream_type="stdout",
                 filename=None,
                 loglevel=None,
                 assertion_log=False,
                 options=None):
        if loglevel is None:
            loglevel = logging.INFO

        self.shouldStop = False
        self.failFast = self.failfast = False
        self.pausable_runner = None

        logging_manager = logging.Manager(
            picklablelogger.RootLogger(logging.WARNING))
        logging_manager.setLoggerClass(picklablelogger.Logger)
        self.logger = logging_manager.getLogger("pausable_unittest")
        self.logger.setLevel(loglevel)
        self.logger.addHandler(
            picklablelogger.PicklableStreamHandler(stream_type))
        if filename is not False:
            self.logger.addHandler(
                picklablelogger.PicklableFileHandler(filename))

        self.assertion_log = assertion_log

        self._stream_type = stream_type
        self._results = []
        self._file = None
        self._running_test = None
        self._total_start_time = None
        self._options = options

    def close_logger(self):
        for handler in self.logger.handlers:
            if hasattr(handler, "close"):
                handler.close()

    def before_pause(self, info):
        if self._running_test:
            self.logger.debug("Pause %s...", self._running_test)
        else:
            self.logger.debug("Pause...")

        for handler in self.logger.handlers:
            if hasattr(handler, "prepare_for_pause"):
                handler.prepare_for_pause()

    def after_pause(self, info):
        for handler in self.logger.handlers:
            if hasattr(handler, "resume_from_pause"):
                handler.resume_from_pause()

        self._writeln("-" * 70)
        if len(self._results) > 0:
            self._writeln("Current results:")
            for result in self._results:
                self._writeln(self.result_text(result))
            self._writeln("-" * 70)

        if self._running_test:
            self.logger.debug("Resume %s...", self._running_test)
        else:
            self.logger.debug("Resume...")

    def _filterResult(self, type):
        return [(x[1], x[2]) for x in self._results if x[0] == type]

    def result_text(self, result):
        result_type = result[0]
        if result_type in {"success", "expected_failure", "skip"}:
            ok = True
        else:
            ok = False

        text = result_type.ljust(7, " ") + ": " + str(result[1])
        if not ok:
            text += "\n" + self._exc_info_to_string(result[2], result[1], 6)
        return text

    def show_results(self):
        self.raw_log("")
        self.raw_log("=" * 70)
        self.raw_log("Results:")
        self.raw_log(" Ran %d tests in %.1fs" % (len(
            self._results), self._total_end_time - self._total_start_time))
        self.raw_log(" success: %4d" % len(self.successes))
        self.raw_log(" failure: %4d" % len(self.failures))
        others = len(self._results) - len(self.successes) - len(self.failures)
        if others > 0:
            self.raw_log(" others:  %4d" % others)
        for i, result in enumerate(self._results):
            self.raw_log(("%4d:[%6.1fs] " % (i, result[3])) +
                         self.result_text(result))
        self.raw_log("=" * 70)

    def addSubTest(self, test, subtest, err):
        u"""Called at the end of a subtest.
        'err' is None if the subtest ended successfully, otherwise it's a
        tuple of values as returned by sys.exc_info().
        """
        if err is None:
            self.addSuccess(subtest, without_log=True)
        else:
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                self.addFailure(subtest, err, without_log=True)
            else:
                self.addError(subtest, err, without_log=True)

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
    def results(self):
        return self._results

    @property
    def testsRun(self):
        return len(self._results)

    def stop(self):
        self.shouldStop = True

    def _outputResult(self):
        pass

    def addResult(self, type, test, err=None):
        time_diff = time.time() - self._start_time
        self._results.append((type, test, err, time_diff))

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
        self._start_time = time.time()
        if self._total_start_time is None:
            self._total_start_time = self._start_time
        self.logger.info("Start %s", desc)

    def stopTest(self, test):
        self._total_end_time = end_time = time.time()
        time_diff = end_time - self._start_time
        desc = self.getDescription(test)
        self.logger.info("End %s (%fs)", desc, time_diff)

    def startTestRun(self, test):
        pass

    def stopTestRun(self, test):
        pass

    def addSuccess(self, test, without_log=False):
        self.addResult("success", test)
        if not without_log:
            self.logger.info("Result: success")

    def addError(self, test, err, without_log=False):
        self.addResult("error", test, err)
        if not without_log:
            self.logger.error("Result: ERROR")
            self.logger.error(self._exc_info_to_string(err, test, 6))

    def addFailure(self, test, err, without_log=False):
        self.addResult("failure", test, err)
        if not without_log:
            self.logger.error("Result: FAILURE")

    def addSkip(self, test, reason):
        self.addResult("skip", test, reason)
        self.logger.info("Result: Skipped {0!r}".format(reason))

    def addExpectedFailure(self, test, err):
        self.addResult("expected_failure", test, err)
        self.logger.info("Result: expected failure")

    def addUnexpectedSuccess(self, test):
        self.addResult("unexpected_success", test)
        self.logger.error("Result: unexpected success")

    def _is_relevant_tb_level(self, tb):
        global_variable_names = tb.tb_frame.f_globals
        tags_for_global_scope = ('__unittest', '__pausable_unittest')
        return any(tag in global_variable_names
                   for tag in tags_for_global_scope)

    def _exc_info_to_string(self, err, test, indent=None):
        u"""Convert a sys.exc_info()-style tuple of values into a string."""
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

        if indent:
            lines = []
            for msg in msgLines:
                lines.extend(msg.rstrip().split("\n"))
            return " " * indent + ("\n" + ' ' * indent).join(lines)
        else:
            return ''.join(msgLines)

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length
