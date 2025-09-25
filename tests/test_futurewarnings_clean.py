import importlib


def test_futurewarnings_clean():
    import warnings

    warnings.simplefilter("error", FutureWarning)

    import jobs.poll_odds  # noqa: F401
    import jobs.compute_clv  # noqa: F401
    import jobs.report_weekly  # noqa: F401
