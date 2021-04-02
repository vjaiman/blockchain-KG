# blockchain-KG
This project is about creating minimal knowledge graph for D1NAMO dataset and create a purpose of use based query (ADA-M ontological matrix) for data requester and matches with the data providers consent (DUO ontology). 

## Usage
To use this tool, you need a running GraphDB instance with the imported triples.
To Transform the D1NAMO dataset into JSON call the utils.createBasicSet(data_root, diabetes, healthy, outpath) in main.py (Line 10)
Then transform it with the rmlmapper to triples.
	you need the jar from here
	then navigate to the output folder and type in the console "java -jar rmlmapper.jar -o output.nt -m mappings.rml.ttl"
Then import output.nt to GraphDB via UI
	Import -> RDF -> Upload RDF files -> chose output.nt -> import
The base url can be retrieved via GraphDB ui.
	Setup -> Repositories -> chose your repository -> copy link from link symbol
Put the base url in main.py

Start the program and it should work

