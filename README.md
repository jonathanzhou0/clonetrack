# CloneTrack
CloneTrack is an application that plans and tracks experiments for the traditional molecular cloning workflow.

## Molecular cloning
Molecular cloning is a very common set of experimental methods in molecular biology that are used to assemble and replicate recombinant DNA molecules. The workflow is generally as follows:

1. Start by purchasing DNA oligos and primers from a vendor.
2. PCR to amplify DNA oligos.
3. Ligate amplified DNA to a vector, creating recombinant plasmids.
4. Transform plasmids into a host organism (usually E. coli) for replication.
5. Isolate replicated plasmids from the host organism

Almost every step of this workflow generates DNA parts which are often labelled and stored for future use. The vision of this application is to have the capability to plan experiments for each step of the cloning workflow given a list of starting materials, and store information about the experiments and DNA parts generated in a database.

## Architecture
This application uses a command line interface, Python back end, and SQLite database.
