"""Plan and track molecular cloning experiments."""

import sqlite3
import re


def initialize_tables():
	"""Initialize sqlite3 tables for experiments."""

	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	cur.execute("""
		CREATE TABLE IF NOT EXISTS oligos
		(index_num, sequence, orientation)
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

	def __init__(self, sequence, orientation):
		"""Initialize."""

		self.sequence = sequence
		self.orientation = orientation
		self.ind = get_next_sql_index('oligos')

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO oligos VALUES (?,?,?)"
		cur.execute(cmd, (self.ind, self.sequence, self.orientation))
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

	types_list = ['oligo', 'pcr', 'ligation', 'transformation', 'miniprep']
	if experiment_type not in types_list:
		raise ValueError("""
		Invalid experiment type! Must be an oligo, pcr, ligation,
		transformation, or miniprep.
		""")
	elif experiment_type == 'oligo':
		try:
			Oligo(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'pcr':
		try:
			PCR(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'ligation':
		try:
			Ligation(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'transformation':
		try:
			Transformation(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"
	elif experiment_type == 'miniprep':
		try:
			Miniprep(*values_tuple)
		except:
			return "ValueError: Something is wrong with your parameters!"


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
		"oligos": ["Index", "Sequence", "Orientation"],
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


