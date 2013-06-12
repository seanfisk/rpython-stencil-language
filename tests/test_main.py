from pytest import fixture

from stencil_lang import metadata
from stencil_lang.main import _main


@fixture(params=['-h', '--help'])
def helparg(request):
    return request.param


@fixture(params=['-V', '--version'])
def versionarg(request):
    return request.param


class TestMain(object):
    def test_help(self, helparg, capsys):
        status_code = _main(['progname', helparg])
        out, err = capsys.readouterr()
        # Should have printed some sort of usage message. We don't
        # need to explicitly test the content of the message.
        assert 'usage' in out
        # Should have used the program name from the argument
        # vector.
        assert 'progname' in out
        # Should exit with zero return code.
        assert status_code == 0

    def test_version(self, versionarg, capsys):
        status_code = _main(['progname', versionarg])
        out, err = capsys.readouterr()
        # Should print version.
        assert out == '{0} {1}\n'.format(metadata.project, metadata.version)
        # Should exit with zero return code.
        assert status_code == 0
