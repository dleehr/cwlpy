# Now instead trying the qiime2-01-import-data.cwl
from cwlgen.import_cwl import parse_cwl
from cwlgen import File, Workflow, SubworkflowFeatureRequirement
from cwlgen.workflow import InputParameter

mkdir_tool = parse_cwl('/Users/dcl9/Code/yaml/bespin-cwl/tools/qiime2/EMPSingleEndSequences-directory.cwl')
import_tool = parse_cwl('/Users/dcl9/Code/yaml/bespin-cwl/tools/qiime2/tools-import.cwl')

w = Workflow()

# Add steps
step1 = w.add('make_import_directory', mkdir_tool, {
    'sequences': File(''),
    'barcodes': File(''),
})
step2 = w.add('make_sequences_artifact', import_tool, {
    'input_path': step1['dir'], 
    'type': InputParameter('sequences_artifact_type', param_type='string'),
})
step2['sequences_artifact'].store()
w.label = 'qiime2 importing data'
w.doc = 'Obtaining and importing data from https://docs.qiime2.org/2018.4/tutorials/moving-pictures/'
w.requirements.append(SubworkflowFeatureRequirement())
w.export()

