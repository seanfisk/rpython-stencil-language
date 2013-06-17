def lit(name):
    """Make a literal token tuple."""
    return (name, name)


def assert_exc_info_msg(exc_info, expected_msg):
    # LHS and RHS intentionally placed so diffs seem correct.
    assert expected_msg == str(exc_info.value)
