"""Plan and track molecular cloning experiments."""

import sqlite3
import re
import datetime
import csv


def initialize_tables():
	"""Initialize sqlite3 tables for experiments."""

	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	cur.execute("""
		CREATE TABLE IF NOT EXISTS oligos
		(index_num, name, sequence, orientation)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS pcrs
		(index_num, date_planned, date_completed, f_primer, r_primer, \
		template, notes, polymerase)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS ligations
		(index_num, date_planned, date_completed, pcr_insert, backbone, \
		notes)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS transformations
		(index_num, date_planned, date_completed, host_strain, plasmid, \
		notes)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS minipreps
		(index_num, date_planned, date_completed, prepped_transformation, \
		concentration, notes)
	""")
	con.commit()
	con.close()


initialize_tables()


def get_next_sql_index(table_name):
	"""Helper function that gets the next index for a
	given SQL table."""

	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	cmd = f"""
	SELECT MAX(index_num) FROM {table_name}
	"""
	cur.execute(cmd)
	ind = cur.fetchone()[0]
	con.close()
	if ind:
		return ind + 1
	else:
		return 1


class Oligo:
	"""Oligo."""

	def __init__(self, name, sequence, orientation):
		"""Initialize."""

		self.name = name
		self.sequence = sequence
		self.orientation = orientation
		self.ind = get_next_sql_index('oligos')

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO oligos VALUES (?,?,?,?)"
		cur.execute(cmd, (self.ind, self.name, self.sequence, self.orientation))
		con.commit()
		con.close()


class Experiment:
	"""Parent class for all experiment types."""

	def __init__(self, date_planned, date_completed='', notes=''):
		"""Initialize."""

		self.date_planned = date_planned
		self.date_completed = date_completed
		self.notes = notes


class PCR(Experiment):
	"""PCR."""

	def __init__(self, date_planned,
				 f_primer, r_primer, template,
				 date_completed='', notes='',
				 polymerase='taq'):
		"""Initialize."""

		super().__init__(date_planned, date_completed, notes)
		self.f_primer = f_primer
		self.r_primer = r_primer
		self.template = template
		self.polymerase = polymerase
		self.ind = get_next_sql_index('pcrs')

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO pcrs VALUES (?,?,?,?,?,?,?,?)"
		cur.execute(cmd, (self.ind, self.date_planned, self.date_completed,
						  self.f_primer, self.r_primer, self.template,
						  self.notes, self.polymerase))
		con.commit()
		con.close()


class Ligation(Experiment):
	"""Ligation."""

	def __init__(self, date_planned,
				 pcr_insert, backbone,
				 date_completed='', notes=''):
		"""Initialize."""

		super().__init__(date_planned, date_completed, notes)
		self.pcr_insert = pcr_insert
		self.backbone = backbone
		self.ind = get_next_sql_index('ligations')

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO ligations VALUES (?,?,?,?,?,?)"
		cur.execute(cmd, (self.ind, self.date_planned, self.date_completed,
						  self.pcr_insert, self.backbone, self.notes))
		con.commit()
		con.close()


class Transformation(Experiment):
	"""Transformation."""

	def __init__(self, date_planned,
				 host_strain, plasmid,
				 date_completed='', notes=''):
		"""Initialize."""

		super().__init__(date_planned, date_completed, notes)
		self.host_strain = host_strain
		self.plasmid = plasmid
		self.ind = get_next_sql_index('transformations')

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO transformations VALUES (?,?,?,?,?,?)"
		cur.execute(cmd, (self.ind, self.date_planned, self.date_completed,
						  self.host_strain, self.plasmid, self.notes))
		con.commit()
		con.close()

class Miniprep(Experiment):
	"""Miniprepped plasmid."""

	def __init__(self, date_planned,
				 prepped_transformation,
				 date_completed='', notes='',
				 concentration=None):
		"""Initialize."""

		super().__init__(date_planned, date_completed, notes)
		self.prepped_transformation = prepped_transformation
		self.concentration = concentration
		self.ind = get_next_sql_index('minipreps')

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO minipreps VALUES (?,?,?,?,?,?)"
		cur.execute(cmd, (self.ind, self.date_planned, self.date_completed,
						  self.prepped_transformation, self.concentration,
						  self.notes))
		con.commit()
		con.close()


def manually_add(experiment_type, values_tuple):
	"""Manually add an experiment to the SQL table."""

	experiment_type = experiment_type.lower()
	types_list = ['oligo', 'pcr', 'ligation', 'transformation', 'miniprep']
	if experiment_type not in types_list:
		raise ValueError("""
		Invalid experiment type! Must be an oligo, pcr, ligation,
		transformation, or miniprep.
		""")
	elif experiment_type == 'oligo':
		try:
			added = Oligo(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'pcr':
		try:
			added = PCR(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'ligation':
		try:
			added = Ligation(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'transformation':
		try:
			added = Transformation(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'miniprep':
		try:
			added = Miniprep(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	return 'Added ' + experiment_type + str(added.ind)


def parse_exp_name(experiment_name):
	"""Helper function that breaks an experiment name into the
	experiment type and SQL table index.
	e.g. pcr1 --> 'pcr', 1"""

	match = re.search('(\w+)(\d+)', experiment_name)
	return (match.groups()[0], int(match.groups()[1]))


def view(experiment_name):
	"""View information about an experiment."""

	(experiment_type, index) = parse_exp_name(experiment_name)
	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	cur.execute(f"""
	SELECT * FROM {experiment_type.lower() + 's'}
	WHERE index_num == {str(index)}
	""")
	experiment_info = cur.fetchone()
	headers = {
		"oligos": ["Index", "Name", "Sequence", "Orientation"],
		"pcrs": ["Index", "Date Planned", "Date Completed",
				 "Forward Primer", "Reverse Primer", "Template", "Notes",
				 "Polymerase"],
		"ligations": ["Index", "Date Planned", "Date Completed", 
					  "PCR Insert", "Backbone", "Notes"],
		"transformations": ["Index", "Date Planned", "Date Completed",
							"Host Strain", "Plasmid", "Notes"],
		"minipreps": ["Index", "Date Planned", "Date Completed",
					  "Transformation", "Concentration", "Notes"]
	}
	header_list = headers[experiment_type.lower() + 's']
	print(*header_list, sep='\t')
	print(*experiment_info, sep='\t')
	con.close()


def edit(experiment_name, col_name, new_entry):
	"""Edit information about an experiment."""

	(experiment_type, index) = parse_exp_name(experiment_name)
	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	cur.execute(f"""
	UPDATE {experiment_type.lower() + 's'}
	SET {col_name} = ?
	WHERE index_num == {str(index)}
	""", (new_entry,))
	con.commit()
	con.close()
	return "Updated experiment!"


def date_to_datetime(datestr):
    """Helper function that converts date given in YYYY-MM-DD string
	to datetime objects."""
    year = int(datestr[0:4])
    month = datestr[5:7]
    if month[0] == '0':
        month = int(month[1])
    else:
        month = int(month)
    day = datestr[8:10]
    if day[0] == '0':
        day = int(day[1])
    else:
        day = int(day)
    return datetime.date(year, month, day)


def load_fasta(filename, oligo_type):
	"""Helper function that processes FASTA formatted.txt files
	containing sequence data for oligos and loads them into the 
	Oligo SQL table while also creating a dict that maps to Oligo
	objects."""

	type_to_orientation = {
		"template" : "doublestranded",
		"f_primer" : "forward",
		"r_primer" : "reverse"
	}
	f = open(filename, 'r')
	names = 0
	seqs = 0
	oligo_list = list()
	for line in f:
		match1 = re.search(">(.+)$", line)
		match2 = re.search("^[^>]+", line)
		if match1:
			oligo_name = match1.group(1)
			names += 1
		if match2:
			oligo_seq = match2.group()
			seqs += 1
			if names == seqs:
				oligo_list.append(Oligo(oligo_name, oligo_seq,
										type_to_orientation[oligo_type]))
			else:
				raise ValueError(".txt file not in FASTA format!")
	f.close()
	return oligo_list


def plan(templates_filename, f_primers_filename, r_primers_filename,
		 backbones_list, start_date, host_strain='E. coli'):
	"""Plan a full set of experiments given FASTA formatted .txt files
	containing sequence data for templates, forward primers, reverse
	primers."""

	templates_list = load_fasta(templates_filename, 'template')
	f_primers_list = load_fasta(f_primers_filename, 'f_primer')
	r_primers_list = load_fasta(r_primers_filename, 'r_primer')
	if len(templates_list) != len(f_primers_list) or \
	len(templates_list) != len(r_primers_list):
		raise ValueError("""
		All .txt files must have the same number of sequences!
		""")
	pcr_list = list()
	for template, f_primer, r_primer in zip(templates_list,
											f_primers_list,
											r_primers_list):
		pcr_list.append(PCR(start_date, f_primer.name, r_primer.name,
							template.name))
	ligation_list = list()
	ligation_date = date_to_datetime(start_date) + datetime.timedelta(days=1)
	for pcr in pcr_list:
		for backbone in backbones_list:
			pcr_index = "PCR" + str(pcr.ind)
			ligation_list.append(Ligation(ligation_date, pcr_index, backbone))
	transformation_list = list()
	transformation_date = date_to_datetime(start_date) + datetime.timedelta(days=2)
	for ligation in ligation_list:
		ligation_index = "Ligation" + str(ligation.ind)
		transformation_list.append(Transformation(transformation_date,
												  host_strain,
												  ligation_index))
	miniprep_list = list()
	miniprep_date = date_to_datetime(start_date) + datetime.timedelta(days=3)
	for transformation in transformation_list:
		transformation_index = "Transformation" + str(transformation.ind)
		miniprep_list.append(Miniprep(miniprep_date, transformation_index))
	for miniprep in miniprep_list:
		print("Miniprep" + str(miniprep.ind))


def export_csv():
	"""Export SQL tables to csv file."""

	headers = {
		"oligos": ["Index", "Name", "Sequence", "Orientation"],
		"pcrs": ["Index", "Date Planned", "Date Completed",
				 "Forward Primer", "Reverse Primer", "Template", "Notes",
				 "Polymerase"],
		"ligations": ["Index", "Date Planned", "Date Completed", 
					  "PCR Insert", "Backbone", "Notes"],
		"transformations": ["Index", "Date Planned", "Date Completed",
							"Host Strain", "Plasmid", "Notes"],
		"minipreps": ["Index", "Date Planned", "Date Completed",
					  "Transformation", "Concentration", "Notes"]
	}
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
	con.close()
	with open('oligos.csv', 'w', newline='') as csvfile:
		datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|',
								quoting=csv.QUOTE_MINIMAL)
		datawriter.writerow(headers['oligos'])
		for oligo in oligos:
			datawriter.writerow(oligo)
	with open('pcrs.csv', 'w', newline='') as csvfile:
		datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|',
								quoting=csv.QUOTE_MINIMAL)
		datawriter.writerow(headers['pcrs'])
		for pcr in pcrs:
			datawriter.writerow(pcr)
	with open('ligations.csv', 'w', newline='') as csvfile:
		datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|',
								quoting=csv.QUOTE_MINIMAL)
		datawriter.writerow(headers['ligations'])
		for ligation in ligations:
			datawriter.writerow(ligation)
	with open('transformations.csv', 'w', newline='') as csvfile:
		datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|',
								quoting=csv.QUOTE_MINIMAL)
		datawriter.writerow(headers['transformations'])
		for transformation in transformations:
			datawriter.writerow(transformation)
	with open('minipreps.csv', 'w', newline='') as csvfile:
		datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|',
								quoting=csv.QUOTE_MINIMAL)
		datawriter.writerow(headers['minipreps'])
		for miniprep in minipreps:
			datawriter.writerow(miniprep)
	return 'Wrote to .csv files!'


def to_do(numdays):
	"""Display all experiments that do not yet have a value in the
	'date_completed' field and have a value within a certain timeframe
	in the 'date_planned' field."""

	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	exp_to_date = dict()
	cur.execute("""
	SELECT index_num, date_planned FROM pcrs WHERE
	date_completed == ''
	""")
	for pcr in cur.fetchall():
		exp_name = 'PCR' + str(pcr[0])
		date_planned = pcr[1]
		exp_to_date[exp_name] = date_to_datetime(date_planned)
	cur.execute("""
	SELECT index_num, date_planned FROM ligations WHERE
	date_completed == ''
	""")
	for ligation in cur.fetchall():
		exp_name = 'Ligation' + str(ligation[0])
		date_planned = ligation[1]
		exp_to_date[exp_name] = date_to_datetime(date_planned)
	cur.execute("""
	SELECT index_num, date_planned FROM transformations WHERE
	date_completed == ''
	""")
	for transformation in cur.fetchall():
		exp_name = 'Transformation' + str(transformation[0])
		date_planned = transformation[1]
		exp_to_date[exp_name] = date_to_datetime(date_planned)
	cur.execute("""
	SELECT index_num, date_planned FROM minipreps WHERE
	date_completed == ''
	""")
	for miniprep in cur.fetchall():
		exp_name = 'Miniprep' + str(miniprep[0])
		date_planned = miniprep[1]
		exp_to_date[exp_name] = date_to_datetime(date_planned)
	con.close()
	to_do_list = list()
	base = datetime.date.today()
	date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
	for name, date in exp_to_date.items():
		if date in date_list:
			to_do_list.append(name)
	return to_do_list

