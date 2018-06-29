# Now instead trying the qiime2-01-import-data.cwl
from cwlgen.import_cwl import parse_cwl
from cwlgen import File, Workflow
from cwlgen.workflow import InputParameter

mkdir_file = '/Users/dcl9/Code/yaml/bespin-cwl/tools/qiime2/EMPSingleEndSequences-directory.cwl'
import_file = '/Users/dcl9/Code/yaml/bespin-cwl/tools/qiime2/tools-import.cwl'

mkdir_tool = parse_cwl(mkdir_file)
import_tool = parse_cwl(import_file)


w = Workflow()
sequences = File('sequences')
barcodes = File('barcodes')

# Add steps
step1 = w.add('make_import_directory', mkdir_tool, {
    'sequences': sequences, 
    'barcodes': barcodes,
})
step2 = w.add('make_sequences_artifact', import_tool, {
    'input_path': step1['dir'], 
    'type': InputParameter('type', param_type='int'),
})
step2['sequences_artifact'].store()

w.export()

