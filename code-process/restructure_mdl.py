from utils import get_tokens,remove_extra_white_spaces
from model_info import model_info
from normalizer import get_normalize_block_name
from combine_all_mdl_files import combine_all_mdl_files
from simulink_preprocess import remove_graphic_component,keep_minimum_component_in_block,floating_points_precision
import argparse
import os

class Restructure_mdl():
    '''
        This class provides utilities to restructure the Mdl Files
    '''

    def __init__(self,simulink_model_name,output_dir):
        '''Instantiate a Restructure_mdl class variables .

                args:
                    simulink_model_name: Name of Simulink model . eg. xyz.mdl
                    output_dir: directory where the bfs restructured simulink model will be saved. This is used for training data
        '''

        self._file = simulink_model_name
        self._output_dir = output_dir+"/output_dir"
        self._structure_to_extract = { 'System','Block','Line'} # Hierarchy level in mdl elements.
        self._tmp_ext = '_TMP'# intermediate file that filters mdl file to only have System block { ... } . Output will be xyz_tmp.mdl
        self._bfs_ext = '_bfs' # output file saved in output directory... file name is xyz_bfs.mdl
        self._tmp_dir = output_dir+'/tmp'
        self._valid_chk_dir = output_dir+'/V_CHK'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not os.path.exists(self._tmp_dir):
            os.mkdir(self._tmp_dir)
        if not os.path.exists(self._output_dir):
            os.mkdir(self._output_dir)
        if not os.path.exists(self._valid_chk_dir):
            os.mkdir(self._valid_chk_dir)

    def update_brace_count(self, line):
        '''
                keep track of brace count

                args:
                    line: line of the file
        '''
        assert(self._brace_count >= 0)
        self._brace_count += line.count('{')
        self._brace_count -= line.count('}')


    def extract_system_blk(self):
        '''
        extracts system block of the Simulink mdl file. Filter out everything else.
        The structure left in the output is Model { Name toy System { Name toy Block { .....} ... }}

        It also changes the name of the Simulink model to toy
        And It also updates the model_info object which keeps track of blocks and its connections. Necessary for bfs restructuring.
        returns:
            filtered list of line in the original file. Each element of the list corresponds to the line in the original file.
        '''
        self._brace_count = 0
        _processed_output = []
        stack = []
        stack_pop_brace_count = 0
        blk_info = ''
        line_info = ''
        mdl_info = model_info()

        with open(self._file, 'r') as file:
            for line in file:
                line = remove_extra_white_spaces(line)
                tokens = get_tokens(line)
                self.update_brace_count(line)
                #if self._brace_count==1 and stack[-1] != "Model":
                    #print("here")
                if "Model" == tokens[0]:
                    stack.append("Model")
                    _processed_output.append(line)
                    while get_tokens(line)[0] != "Name":
                        line = remove_extra_white_spaces(next(file))
                    _processed_output.append("Name toy")

                elif tokens[0] == "System" and stack[-1] == "Model":
                    stack_pop_brace_count += 1
                    stack.append(tokens[0])
                elif tokens[0] in self._structure_to_extract and stack[-1] != "Model":
                    stack_pop_brace_count += 1
                    stack.append(tokens[0])
                if stack[-1] in self._structure_to_extract:
                    if tokens[0] == "System":
                        _processed_output.append(line)
                        while get_tokens(line)[0] != "Name":
                            line = remove_extra_white_spaces(next(file))
                        _processed_output.append("Name toy")
                        while get_tokens(line)[0] != 'Block':
                            line = remove_extra_white_spaces(next(file))
                        stack.append('Block')
                        _processed_output.append(line)
                        #print(next_line)
                    else:
                        _processed_output.append(line)
                    if stack[-1] == "Block":

                        blk_info += line + "\n"
                    elif stack[-1] == "Line":
                        line_info += line + "\n"

                if stack_pop_brace_count == self._brace_count:
                    val = stack.pop()
                    if val == "Block":
                        #print(blk_info)
                        mdl_info.update_blk_info(blk_info)
                        blk_info = ''

                    elif val == "Line":
                        mdl_info.update_line_info(line_info)
                        line_info = ''
                    stack_pop_brace_count -= 1
                    if not stack:
                        try:
                            while True:
                                next_line = remove_extra_white_spaces(next(file))
                                _processed_output.append(next_line)
                        except StopIteration:
                            break
                    elif stack[-1] == "Model":
                        _processed_output.append(line)

        return _processed_output, mdl_info
    def restructure_bfs_to_original(self):
        tmp_filename = self._file.split('/')[-1].split('.')[0] + self._tmp_ext + '.mdl'
        tmp_path = os.path.join(self._tmp_dir, tmp_filename)
        output_filename = tmp_filename.replace('_TMP', '_vbfs')
        valid_chk_path = os.path.join(self._valid_chk_dir, output_filename)

        tmp_output, model_info = self.extract_system_blk()
        self.save_to_file(tmp_path, tmp_output)

        bfs_valid_output = self.bfs_ordering_validation(model_info)
        self.save_to_file(valid_chk_path, bfs_valid_output)


    def restructure_single_mdl(self):
        '''
        Entry point for restructuring. Calls functions in a sequence.
        Each functions returned value is the input parameter to next function in the sequence.
        '''

        tmp_filename = self._file.split('/')[-1] .split('.')[0]+ self._tmp_ext + '.mdl'
        output_filename = self._file.split('/')[-1] .split('.')[0]+ self._bfs_ext + '.mdl'

        tmp_path  = os.path.join(self._tmp_dir,tmp_filename)
        output_path = os.path.join(self._output_dir,output_filename)
        output_filename = output_filename.replace('_bfs','_vbfs')
        #print(output_filename)
        valid_chk_path  = os.path.join(self._valid_chk_dir,output_filename)

        tmp_output,model_info = self.extract_system_blk()
        self.save_to_file(tmp_path,  tmp_output)



        src, dest = model_info.get_src_dst()
        source_block = list(set(src).difference(set(dest)))
        output,org_norm_name_dict = self.bfs_ordering_new(source_block, model_info)
        #print("\n".join(output))

        output = floating_points_precision("\n".join(output))
        #print(output)
        output = remove_graphic_component(output)
        self.save_to_file(output_path,output,org_norm_name_dict)
        #self.save_to_file(output_path, output)
        self._file = output_path
        tmp_output, model_info = self.extract_system_blk()

        bfs_valid_output = self.bfs_ordering_validation(model_info)
        self.save_to_file(valid_chk_path, bfs_valid_output)

        #output = keep_minimum_component_in_block("\n".join(bfs_valid_output))
        #print("\n".join(output))
        #print(output)

    def save_to_file(self,  path, tmp_output,org_norm_name_dict = None):
        '''
        saves/write the list of line to a file.
        args:
            path : full path location of the file to which tmp_output is to be saved
            tmp_output: list of lines . Each element of the list corresponds to the line in the original file.
            org_norm_name_dict: dictionary with key : block name and value : normalized block name. Example clblk1 : a, clblk2: b and so on
        '''
        tmp = '\n'.join(tmp_output)
        if org_norm_name_dict is not None:
            for k,v in org_norm_name_dict.items():
                tmp = tmp.replace(k,v)

        with open(path,'w') as r:
            r.write(tmp)

    def bfs_ordering_validation(self,mdl_info):
        '''
        converts the BFS ordered Simulink file back to Simulink acceptable format: where Block {} defination comes first and then Line {} defination
        Caveat: Block with Block Type Outport have to be defined end of the all other block defination arranged in ascending order based on its port number
        while BLock Type Inport has to be defined beginning of the Block defination .
        Generated model may not have Port number.--> Port "2". In that case add port number
        args:
            path: full path of the Simulink model file.

        returns :
            list of lines where each element corresponds to the line in the processed file.
        '''
        blk_lst, line_lst = mdl_info.get_write_ready_blk_conn_list()
        _processed_output = ["Model {", "Name toy", "System {", "Name toy"]
        _processed_output += blk_lst
        _processed_output += line_lst
        _processed_output += ['}','}']
        return _processed_output

    def bfs_ordering_new(self, source_block, model_info):
        blk_names = [k for k in model_info.blk_info.keys()]
        orig_normalized_blk_names = {}
        name_counter = 1
        output = ["Model {", "Name toy", "System {", "Name toy"]
        unique_lines_added = set()

        while len(source_block) != 0 or len(blk_names)!=0:
            queue = []
            if len(source_block) != 0:
                queue.append(source_block[-1])
            elif len(blk_names)!=0:
                queue.append(blk_names[-1])
            while len(queue) != 0 :
                blk_visited = queue.pop(0)
                if blk_visited in blk_names:
                    if blk_visited not in orig_normalized_blk_names:
                        orig_normalized_blk_names[blk_visited] = get_normalize_block_name(name_counter)
                        name_counter += 1
                    block_code = model_info.blk_info[blk_visited]
                    output.append(block_code) # adding block code
                    blk_names.remove(blk_visited)
                    if blk_visited in model_info.graph:
                        for dest_edge in model_info.graph[blk_visited]:
                            (dest, edge) = dest_edge
                            if edge not in unique_lines_added:
                                output.append(edge)
                            unique_lines_added.add(edge)
                            for d in dest:
                                if d in blk_names:
                                    queue.append(d)
                    if blk_visited in model_info.graph_dest:
                        for src_edge in model_info.graph_dest[blk_visited]:
                            (src, edge) = src_edge
                            if edge not in unique_lines_added:
                                output.append(edge)
                            unique_lines_added.add(edge)
                            if src in blk_names:
                                queue.append(src)

                if blk_visited in source_block:
                    source_block.remove(blk_visited)
        output += ['}','}']
        return output,orig_normalized_blk_names

parser = argparse.ArgumentParser(
    description='combine-all-model-to-single-file',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dataset_dir', metavar='PATH', type=str, required=True, help='directory')
parser.add_argument('--code_rewrite', default=False, action='store_true', help='Do Code Rewriting')
args = parser.parse_args()

count = 0
directory = args.dataset_dir
src_folder  = directory.replace('/','')
output_dir='../Experiments/Restructure'
output_dir = (os.path.join(output_dir,src_folder))
for files in os.listdir(directory):
    count +=1

    print(count, " : ", files)
    try:
        processor = Restructure_mdl(os.path.join(directory,files),output_dir)
        if args.code_rewrite:
                processor.restructure_single_mdl()
                combine_all_mdl_files(os.path.join(output_dir,"output_dir"))
        else:
                processor.restructure_bfs_to_original()
    except UnicodeDecodeError:
        continue
    except Exception as e:
        print(e)
        print("Error Processing : ", files)
        continue


