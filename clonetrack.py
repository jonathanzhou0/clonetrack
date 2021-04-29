"""Plan and track molecular cloning experiments."""

import sqlite3


def initialize_tables():
	"""Initialize sqlite3 tables for experiments."""

	con = sqlite3.connect('clonetrack.db')
	cur = con.cursor()
	cur.execute("""
		CREATE TABLE IF NOT EXISTS oligos
		(name, sequence, orientation)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS pcrs
		(name, date_planned, f_primer, r_primer, template, \
		date_completed, notes, polymerase)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS ligations
		(name, date_planned, pcr_insert, backbone, \
		date_completed, notes)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS transformations
		(name, date_planned, host_strain, plasmid, \
		date_completed, notes)
	""")
	cur.execute("""
		CREATE TABLE IF NOT EXISTS minipreps
		(name, date_planned, prepped_transformation, \
		date_completed, notes, concentration)
	""")
	con.commit()
	con.close()


initialize_tables()


class Oligo:
	"""Oligo."""

	def __init__(self, name, sequence, orientation):
		"""Initialize."""

		self.name = name
		self.sequence = sequence
		self.orientation = orientation

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO oligos VALUES (?,?,?)"
		cur.execute(cmd, (self.name, self.sequence, self.orientation))
		con.commit()
		con.close()


class Experiment:
	"""Parent class for all experiment types."""

	def __init__(self, name, date_planned, date_completed='', notes=''):
		"""Initialize."""

		self.name = name
		self.date_planned = date_planned
		self.date_completed = date_completed
		self.notes = notes


class PCR(Experiment):
	"""PCR."""

	def __init__(self, name, date_planned,
				 f_primer, r_primer, template,
				 date_completed='', notes='',
				 polymerase='taq'):
		"""Initialize."""

		super().__init__(name, date_planned, date_completed, notes)
		self.f_primer = f_primer
		self.r_primer = r_primer
		self.template = template
		self.polymerase = polymerase

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO pcrs VALUES (?,?,?,?,?,?,?,?)"
		cur.execute(cmd, (self.name, self.date_planned, self.date_completed,
						  self.f_primer, self.r_primer, self.template,
						  self.notes, self.polymerase))
		con.commit()
		con.close()


class Ligation(Experiment):
	"""Ligation."""

	def __init__(self, name, date_planned,
				 pcr_insert, backbone,
				 date_completed='', notes=''):
		"""Initialize."""

		super().__init__(name, date_planned, date_completed, notes)
		self.pcr_insert = pcr_insert
		self.backbone = backbone

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO ligations VALUES (?,?,?,?,?,?)"
		cur.execute(cmd, (self.name, self.date_planned, self.date_completed,
						  self.pcr_insert, self.backbone, self.notes))
		con.commit()
		con.close()


class Transformation(Experiment):
	"""Transformation."""

	def __init__(self, name, date_planned,
				 host_strain, plasmid,
				 date_completed='', notes=''):
		"""Initialize."""

		super().__init__(name, date_planned, date_completed, notes)
		self.host_strain = host_strain
		self.plasmid = plasmid

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO transformations VALUES (?,?,?,?,?,?)"
		cur.execute(cmd, (self.name, self.date_planned, self.date_completed,
						  self.host_strain, self.plasmid, self.notes))
		con.commit()
		con.close()

class Miniprep(Experiment):
	"""Miniprepped plasmid."""

	def __init__(self, name, date_planned,
				 prepped_transformation,
				 date_completed='', notes='',
				 concentration=None):
		"""Initialize."""

		super().__init__(name, date_planned, date_completed, notes)
		self.prepped_transformation = prepped_transformation
		self.concentration = concentration

		con = sqlite3.connect('clonetrack.db')
		cur = con.cursor()
		cmd = "INSERT INTO minipreps VALUES (?,?,?,?,?,?)"
		cur.execute(cmd, (self.name, self.date_planned, self.date_completed,
						  self.prepped_transformation, self.concentration,
						  self.notes))
		con.commit()
		con.close()

