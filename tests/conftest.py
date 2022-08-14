from pathlib import Path
import rklib

def pytest_report_header(config):
    """Add information on the package version used in the tests.
    """
    modpath = Path(rklib.__file__).resolve().parent
    return [ "rklib: %s" % (rklib.__version__),
             "       %s" % (modpath)]
