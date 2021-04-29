"""Test clonetrack."""

import sqlite3
import clonetrack as ct
import re
import datetime
import csv


def test_manually_add():
    """Test manually_add()."""

    ct.manually_add('oligo', ('JZ1F', 'GAGA', 'forward'))
    ct.manually_add('pcr', ('2021-05-01', 'ATATAT', 'GAGAGA', 'GCGCGC'))
    ct.manually_add('ligation', ('2021-05-01', 'PCR1', 'Template1'))
    ct.manually_add('transformation', ('2021-05-01', 'Ecoli', 'Ligation1'))
    ct.manually_add('miniprep', ('2021-05-01', 'Transformation1'))
    ct.manually_add('oligo', ('JZ1R', 'AGAG', 'reverse'))
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
    assert oligos == [(1, 'JZ1F', 'GAGA', 'forward'), (2, 'JZ1R', 'AGAG', 'reverse')]
    assert pcrs == [(1, '2021-05-01', '', 'ATATAT', 'GAGAGA', 'GCGCGC',
                    '', 'taq')]
    assert ligations == [(1, '2021-05-01', '', 'PCR1', 'Template1', '')]
    assert transformations == [(1, '2021-05-01', '', 'Ecoli', 'Ligation1',
                               '')]
    assert minipreps == [(1, '2021-05-01', '', 'Transformation1', None, '')]
    con.commit()
    con.close()


def test_edit():
    """Test edit()."""

    ct.edit('PCR1', 'date_completed', '2021-05-05')
    con = sqlite3.connect('clonetrack.db')
    cur = con.cursor()
    cur.execute("""
    SELECT date_completed FROM pcrs
    WHERE index_num == 1
    """)
    assert cur.fetchone()[0] == '2021-05-05'
    con.commit()
    con.close()


def test_plan():
    """Test plan()."""

    f = open('test_templates.txt', 'w')
    f.write('>Template1')
    f.write('\nGGGGGGGGGGGGGGG')
    f.write('\n>Template2')
    f.write('\nAAAAAAAAAAAAAAA')
    f.write('\n>Template1')
    f.write('\nGGGGGGGGGGGGGGG')
    f.close()

    f = open('test_f_primers.txt', 'w')
    f.write('>JZ1-F')
    f.write('\nGGGG')
    f.write('\n>JZ2-F')
    f.write('\nCCCC')
    f.write('\n>JZ3-F')
    f.write('\nAAAA')
    f.close()

    f = open('test_r_primers.txt', 'w')
    f.write('>JZ1-R')
    f.write('\nCCCC')
    f.write('\n>JZ2-R')
    f.write('\nGGGG')
    f.write('\n>JZ3-R')
    f.write('\nTTTT')
    f.close()

    backbones_list = ['Backbone1', 'Backbone2']
    start_date = '2021-06-01'

    ct.plan('test_templates.txt', 'test_f_primers.txt',
            'test_r_primers.txt', backbones_list, start_date)

    con = sqlite3.connect('clonetrack.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM oligos WHERE index_num > 2")
    num_oligos = len(cur.fetchall())
    cur.execute("SELECT * FROM pcrs WHERE index_num > 1")
    num_pcrs = len(cur.fetchall())
    cur.execute("SELECT * FROM ligations WHERE index_num > 1")
    num_ligations = len(cur.fetchall())
    cur.execute("SELECT * FROM transformations WHERE index_num > 1")
    num_transformations = len(cur.fetchall())
    cur.execute("SELECT * FROM minipreps WHERE index_num > 1")
    num_minipreps = len(cur.fetchall())
    cur.execute("""
    SELECT prepped_transformation FROM minipreps WHERE
    index_num == 2
    """)
    miniprep2_trans = cur.fetchone()[0]

    assert num_oligos == 9
    assert num_pcrs == 3
    assert num_ligations == 6
    assert num_transformations == 6
    assert num_minipreps == 6
    assert miniprep2_trans == 'Transformation2'


def test_export_csv():
    """Test export_csv()."""

    ct.export_csv()
    idx = -1
    with open('oligos.csv', newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in datareader:
            idx += 1
            if idx == 0:
                continue
            assert int(row[0]) == idx
    idx = -1
    with open('pcrs.csv', newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in datareader:
            idx += 1
            if idx == 0:
                continue
            assert int(row[0]) == idx
    idx = -1
    with open('ligations.csv', newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in datareader:
            idx += 1
            if idx == 0:
                continue
            assert int(row[0]) == idx
    idx = -1
    with open('transformations.csv', newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in datareader:
            idx += 1
            if idx == 0:
                continue
            assert int(row[0]) == idx
    idx = -1
    with open('minipreps.csv', newline='') as csvfile:
        datareader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in datareader:
            idx += 1
            if idx == 0:
                continue
            assert int(row[0]) == idx


def test_to_do():
    """Test to_do()."""

    assert ct.to_do(0) == []
    assert len(ct.to_do(7)) == 3
    assert len(ct.to_do(40)) == 24
    
