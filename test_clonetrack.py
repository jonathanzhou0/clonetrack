"""Test clonetrack."""

import sqlite3
import clonetrack as ct
import re


def test_manually_add():
    """Test manually_add()."""

    ct.manually_add('oligo', ('GAGA', 'forward'))
    ct.manually_add('pcr', ('05-01-2021', 'ATATAT', 'GAGAGA', 'GCGCGC'))
    ct.manually_add('ligation', ('05-01-2021', 'PCR1', 'Template1'))
    ct.manually_add('transformation', ('05-01-2021', 'Ecoli', 'Ligation1'))
    ct.manually_add('miniprep', ('05-01-2021', 'Transformation1'))
    ct.manually_add('oligo', ('AGAG', 'reverse'))
    con = sqlite3.connect('clonetrack.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM oligos')
    oligos = cur.fetchall()
    cur.execute('SELECT * FROM pcrs')
    pcrs = cur.fetchall()
    cur.execute('SELECT * FROM ligations')
    ligations = cur.fetchall()
    cur.execute('SELECT * FROM transformations')
    transformations = cur.fetchall()
    cur.execute('SELECT * FROM minipreps')
    minipreps = cur.fetchall()
    assert oligos == [(1, 'GAGA', 'forward'), (2, 'AGAG', 'reverse')]
    assert pcrs == [(1, '05-01-2021', '', 'ATATAT', 'GAGAGA', 'GCGCGC',
                    '', 'taq')]
    assert ligations == [(1, '05-01-2021', '', 'PCR1', 'Template1', '')]
    assert transformations == [(1, '05-01-2021', '', 'Ecoli', 'Ligation1',
                               '')]
    assert minipreps == [(1, '05-01-2021', '', 'Transformation1', None, '')]
    con.commit()
    con.close()