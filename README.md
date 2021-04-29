# CloneTrack
CloneTrack is a Python library that plans and tracks experiments for the traditional molecular cloning workflow.

## Molecular cloning
Molecular cloning is a very common set of experimental methods in molecular biology that is used to assemble and replicate recombinant DNA molecules. The workflow is generally as follows:

1. Start by purchasing DNA oligos and primers from a vendor.
2. PCR to amplify DNA oligos.
3. Ligate amplified DNA to a vector, creating recombinant plasmids.
4. Transform plasmids into a host organism (usually E. coli) for replication.
5. Isolate replicated plasmids from the host organism

Almost every step of this workflow generates DNA parts which are often labelled and stored for future use. The vision of this application is to have the capability to plan experiments for each step of the cloning workflow given a list of starting materials, and store information about the experiments and DNA parts generated in a database.

## Architecture
This is a Python library that makes use of a SQLite database.

## Documentation

### Installation

Clone this git repository using the following bash command:

```bash
git clone git@github.com:jonathanzhou0/clonetrack.git
```

### Tests

IMPORTANT: The tests use the same database as the actual library, so tests must be run with an empty database (delete 'clonetrack.db') in order to work. Tests can be run using test_clonetrack.py and the pytest module using the following commands:

```bash
pip install pytest
python -m pytest -s
```

### manually_add

This function is used to manually add an experiment/oligo to the database. There are five types of data that are supported: Oligo, PCR, Ligation, Transformation, and Miniprep. The syntax is as follows:

```python
clonetrack.manually_add('oligo', ('name', 'sequence', 'orientation'))
clonetrack.manually_add('pcr', ('date_planned', 'f_primer', 'r_primer', 'oligo_template', 'date_completed', 'notes', 'polymerase'))
clonetrack.manually_add('ligation', ('date_planned', 'pcr_insert', 'backbone', 'date_completed', 'notes'))
clonetrack.manually_add('transformation', ('date_planned', 'host_strain', 'plasmid', 'date_completed', 'notes'))
clonetrack.manually_add('miniprep', ('date_planned','prepped_transformation', 'date_completed', 'notes', 'concentration'))
```

The first argument is a string that describes the type of data being added. The second is a tuple containing information about the data. Different data types require different tuple lengths. Also, some arguments are optional: date_completed, notes, polymerase, and concentration are all optional arguments that are filled with empty strings by default.

In addition to storing the data, the function also returns a unique name which is used to query the data later. The naming convention is simply the data type and then a number, e.g. Oligo1, Oligo2, Oligo3, PCR1, PCR2, PCR3 ....

### view

This function is used to view information about a specific experiment. The syntax is as follows:

```python
clonetrack.view('PCR1')
```

The only argument is the experiment name that is returned by manually_add.

### edit

This function is used to edit information about a specific experiment. The syntax is as follows:

```python
clonetrack.edit('PCR1', 'date_completed', '05-05-2021')
```

The first argument is the name of the experiment to be edited; the second is the column of data to edit; and the third is the new information to use. Note that this function OVERWRITES any data that was already in the database.

### plan

This function is used to automatically add and plan experiments that take a set of oligos and backbones through the entire cloning workflow. It requires three .txt files which must be in FASTA format - examples can be found in the test files included in this repository. In FASTA format, each sequence is 2 lines long - the first line is a header line, which starts with a ">" and includes the name of the sequence; and the second line is the sequence. The syntax of the function is as follows:

```python
clonetrack.plan('templates.txt', 'f_primers.txt', 'r_primers.txt', backbones_list, start_date, host_strain)
```

The first three arguments are filenames for the FASTA .txt files. The fourth argument is a list of strings where each string is the name of a plasmid backbone. The fifth argument is the desired start date for the experiment - the function will automatically assign experiments to be done on successive days from each other. The sixth argument is optional and defaults to "E. coli", the most popular host strain for transformations in molecular biology.

The function requires that each FASTA .txt file has the same number of sequences, and PCRS are planned such that the first sequence in the template file is PCR'd with the first sequence in the primer files, and so on with the second, third, and so forth. For ligations, the function assumes that each PCR product will be ligated with ALL backbones included in the backbone list.

### export_csv

This function exports the five databases as five .csv files. The syntax is as follows:

```python
clonetrack.export_csv()
```

No arguments are needed.

### to_do

This function returns a list of experiments that have not yet been completed, and are scheduled to be done within the next x days. The syntax is as follows:

```python
clonetrack.to_do(numdays)
```

The function takes one argument numdays, which is an integer representing the number of days to look forward to find planned experiments.