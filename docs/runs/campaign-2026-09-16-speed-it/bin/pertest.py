#!/usr/bin/env python3
"""Per-test wall times in a single pass (custom TestResult)."""
import sys, time, unittest

pattern = sys.argv[1]
suite = unittest.TestLoader().discover("tests", pattern=pattern)

class T(unittest.TextTestResult):
    def startTest(self, t):
        self._s = time.time()
        super().startTest(t)
    def stopTest(self, t):
        super().stopTest(t)
        print(f"{time.time() - self._s:7.2f}s {t.id()}", flush=True)

r = unittest.TextTestRunner(resultclass=T, verbosity=0).run(suite)
print(f"ran={r.testsRun} failures={len(r.failures)} errors={len(r.errors)}")
