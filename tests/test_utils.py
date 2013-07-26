from stencil_lang.utils import rjust, ljust


class TestRjust(object):
    def test_width_larger_than_text_size(self):
        assert rjust('abcd', 10) == '      abcd'

    def test_width_equal_to_text_size(self):
        assert rjust('Just a test', 11) == 'Just a test'

    def test_width_smaller_than_text_size(self):
        assert rjust('hello there', 5) == 'hello there'


class TestLjust(object):
    def test_width_larger_than_text_size(self):
        assert ljust('abcd', 10) == 'abcd      '

    def test_width_equal_to_text_size(self):
        assert ljust('Just a test', 11) == 'Just a test'

    def test_width_smaller_than_text_size(self):
        assert ljust('hello there', 5) == 'hello there'
