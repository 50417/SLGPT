from typing import List
from utils import get_tokens
import re
def remove_graphic_component(text: str) -> List:
    '''
        removes components that are not necessary for the compilation of Simulink model. The component are auto generated when saved in Simulink.
        args:
            text: Simulink model file.
        returns :
            list of lines where line containing remove_list are filtered
    '''
    lines = []
    remove_list = ["Position","ZOrder","SID","Points"]
    for line in text.split("\n"):
        line = line.lstrip()
        if line.startswith(tuple(remove_list)) or len(line)==0:
            continue
        lines.append(line)
    return lines


def keep_minimum_component_in_block(text: str) -> List:
    lines = []
    add_block_comp_list = ["BlockType","Name","Ports","SourceBlock","SourceType"]
    brace_count = 0
    for line in text.split("\n"):
        line = line.strip()
        if len(line) == 0:
            continue
        tok = get_tokens(line)
        if "Block" in tok and "{" in tok:
            brace_count = 1
            lines.append(line)
        elif "}" in tok:
            brace_count = max(0, brace_count - 1)
            if brace_count != 0:
                lines.append(line)
        if brace_count == 0:
            lines.append(line)

        else:
            if line.startswith(tuple(add_block_comp_list)):
                lines.append(line)


    return lines

def floating_points_precision(text:str) -> str:
    lst = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    for i in lst:
        if len(i) > 5:
            text = text.replace(i, i[:4])
    return text

# import os
# directory = '/home/sls6964xx/Documents/GPT2/gpt-2/preprocessor/output'
# count = 1
# if not os.path.exists("Minimum"):
#     os.mkdir("Minimum")
# for files in os.listdir(directory):
#      count +=1
#      print(count, " : ", files)
#      with open(directory + "/" + files,"r") as file:
#          output = keep_minimum_component_in_block(file.read())
#      tmp_path = os.path.join("Minimum", files)
#      with open(tmp_path, 'w') as r:
#          r.write("\n".join(output))
