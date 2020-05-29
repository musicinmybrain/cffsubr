import io
import pathlib
from fontTools import ttLib
import cffsubr
import pytest


DATA_DIR = pathlib.Path(__file__).parent / "data"


def load_test_font(name):
    font = ttLib.TTFont()
    font.importXML(DATA_DIR / name)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return ttLib.TTFont(buf)


class TestSubroutinize:
    @pytest.mark.parametrize(
        "testfile, table_tag",
        [
            ("SourceSansPro-Regular.subset.ttx", "CFF "),
            ("SourceSansVariable-Roman.subset.ttx", "CFF2"),
        ],
    )
    def test_output_same_cff_version(self, testfile, table_tag):
        font = load_test_font(testfile)

        assert cffsubr._sniff_cff_table_format(font) == table_tag

        cffsubr.subroutinize(font)

        assert cffsubr._sniff_cff_table_format(font) == table_tag

    @pytest.mark.parametrize(
        "testfile, cff_version",
        [
            ("SourceSansPro-Regular.subset.ttx", 2),
            ("SourceSansVariable-Roman.subset.ttx", 1),
        ],
    )
    def test_output_different_cff_version(self, testfile, cff_version):
        font = load_test_font(testfile)
        table_tag = cffsubr._sniff_cff_table_format(font)

        cffsubr.subroutinize(font, cff_version=cff_version)

        assert cffsubr._sniff_cff_table_format(font) != table_tag

    @pytest.mark.parametrize(
        "testfile",
        ["SourceSansPro-Regular.subset.ttx", "SourceSansVariable-Roman.subset.ttx"],
    )
    def test_inplace(self, testfile):
        font = load_test_font(testfile)

        font2 = cffsubr.subroutinize(font, inplace=False)
        assert font is not font2

        font3 = cffsubr.subroutinize(font, inplace=True)
        assert font3 is font

    def test_keep_glyph_names(self):
        font = load_test_font("SourceSansPro-Regular.subset.ttx")
        glyph_order = font.getGlyphOrder()

        assert font["post"].formatType == 3.0
        assert font["post"].glyphOrder is None

        cffsubr.subroutinize(font, cff_version=2)

        assert font["post"].formatType == 2.0
        assert font["post"].glyphOrder == glyph_order

        buf = io.BytesIO()
        font.save(buf)
        buf.seek(0)
        font2 = ttLib.TTFont(buf)

        assert font2.getGlyphOrder() == glyph_order

    def test_drop_glyph_names(self):
        font = load_test_font("SourceSansPro-Regular.subset.ttx")
        glyph_order = font.getGlyphOrder()

        assert font["post"].formatType == 3.0
        assert font["post"].glyphOrder is None

        cffsubr.subroutinize(font, cff_version=2, keep_glyph_names=False)

        assert font["post"].formatType == 3.0
        assert font["post"].glyphOrder is None

        buf = io.BytesIO()
        font.save(buf)
        buf.seek(0)
        font2 = ttLib.TTFont(buf)

        assert font2.getGlyphOrder() != glyph_order