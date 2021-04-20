import re
from utils import get_tokens, blk_name_check
class model_info():
    '''
        class to maintain the Simulink model info as a graph.
    '''
    def __init__(self):
        ''' destination block name is a list to account for the lines with branch
        Assumption . A line with branch will only have single source/. Thats why source source block is string'''
        self.graph = {} # dictionary that maintains Simulink model as a graph in adjacency matrix where keys = source block name  and values = (dest block name, line code)
        self.blk_info = {} # dictionary to maintain block code corresponding to block name. key = block name and value = block code.
        self.graph_dest = {} # dictionary to maintain Simulink model as a graph in adjaceny matrix where key = destination block name and values = (Source Block name, otherdestination, line code)

    def get_src_dst(self):
        '''
         returns: Simulink source block and Simulink sink blocks
        '''
        source_blk =  [blk_name for blk_name in self.graph.keys()]
        dst_blk = [dest for dest_code in self.graph.values() for dest_list,code in dest_code for dest in dest_list]
        return source_blk,dst_blk

    def fix_outport(self,outport_blk_code_sorted):
        return_list = []
        for idx in range(len(outport_blk_code_sorted)):
            if idx == 0:
                return_list.append(outport_blk_code_sorted[idx])
                continue
            code = outport_blk_code_sorted[idx]
            has_port_number = False
            for line in code.split("\n"):
                tok = get_tokens(line)
                if "Port" in tok:
                    has_port_number = True
                    param, val = tok[0], tok[1]
                    port_num = re.findall(r"[0-9]+", val)
                    code.replace(port_num[0],str(idx+1))
                    return_list.append(code)
                    break
            if not has_port_number:
                c_idx = code.index("IconDisplay")
                code = code[:c_idx] + "\nPort \"" + str(idx+1) + '"\n' + code[c_idx:]
                return_list.append(code)
        return return_list



    def get_write_ready_blk_conn_list(self):
        '''
         this function is used to structure a Simulink model file in bfs format to Simulink standard format
         returns:
            list of block code and line codes in Simulink standard format.
        '''
        all_blks = [k for k in self.blk_info.keys()]
        all_blks_vist = all_blks.copy()
        blk_code_lst = []
        outport_blk_code = []

        port_number_order = []
        outport_blk_name = []
        for blk in all_blks_vist:
            code = self.blk_info[blk]

            if "BlockType Outport" in code:
                outport_blk_name.append(blk)
                first_outport = True
                for line in code.split("\n"):
                    tok = get_tokens(line)

                    if "Port" in tok:
                        param, val = tok[0], tok[1]
                        first_outport = False
                        port_num = re.findall(r"[0-9]+",val)
                        if len(port_num) ==0:
                            continue
                        port_num = int(port_num[0])
                        outport_blk_code.append(code)
                        port_number_order.append(port_num)
                if first_outport:
                    outport_blk_code.append(code)
                    port_number_order.append(-1)


            else:
                blk_code_lst.append(code)
                all_blks.remove(blk)
        sorted_idx = [i[0] for i in sorted(enumerate(port_number_order),key= lambda x:x[1])]
        outport_blk_code_sorted = [ outport_blk_code[k] for k in sorted_idx]

        outport_blk_code_sorted = self.fix_outport(outport_blk_code_sorted)
        for blk in all_blks:
            if blk in outport_blk_name:
                continue
            code = self.blk_info[blk]
            blk_code_lst.append(code)
        blk_code_lst = blk_code_lst + outport_blk_code_sorted

        # port_number_order.sort()
        # for p in port_number_order:
        #     code = outport_blk_code_port[p]
        #     blk_code_lst.append(code)


        line_code_lst = [code for dest_code in self.graph.values() for dest_list,code in dest_code]
        return blk_code_lst, line_code_lst

    def update_line_info(self,line_code): # edges
        '''
            updates the model_info obj attribute:  self.graph.
            args:
                line_code : line code from Simulink model file
        '''
        src_blk = ''
        dest_blk = []

        lines = line_code.split("\n")
        for idx in range(len(lines)):
            tokens = get_tokens(lines[idx])
            if (tokens[0] == "SrcBlock"):

                src_blk_name = tokens[1]
                while  not blk_name_check(src_blk_name):
                    idx += 1
                    src_blk_name += lines[idx]
                    #print(src_blk_name)
                src_blk = src_blk_name
            elif (tokens[0] == "DstBlock"):
                dest_blk.append(tokens[1])
        if src_blk in self.graph:
            self.graph[src_blk].append((dest_blk,line_code))
        else:
            self.graph[src_blk] = [(dest_blk,line_code)]
        for b in dest_blk:
            if b in self.graph_dest:
                self.graph_dest[b].append((src_blk,line_code))
            else:
                self.graph_dest[b] = [(src_blk,line_code)]

    def update_blk_info(self, blk_code):

        '''
            updates the model_info obj attribute:  self.blk_info.
            args:
                blk_code : blk code from Simulink model file
        '''

        lines  =   blk_code.split("\n")
        for idx in range(len(lines)):
            tokens = get_tokens(lines[idx])
            if (tokens[0] == "Name"):
                blk_name = tokens[1]
                while not blk_name_check(blk_name):
                    idx += 1
                    blk_name += lines[idx]
                if blk_name not in self.blk_info:
                    self.blk_info[blk_name] = blk_code
        #print(self.blk_info)
'''
m = model_info()
m.update_line_info("""    Line {
      ZOrder		      5
      SrcBlock		      "cfblk5"
      SrcPort		      1
      Points		      [0, 0]
      Branch {
	ZOrder			1
	Points			[0, -35; -720, 0]
	DstBlock		"cfblk1"
	DstPort			1
      }
      Branch {
	ZOrder			6
	Points			[0, -35; -400, 0]
	DstBlock		"cfblk3"
	DstPort			1
      }
    }""")

m.update_line_info("""       Line {
      ZOrder		      2
      SrcBlock		      "Complex to\nMagnitude-Angle"
      SrcPort		      1
      Points		      [90, 0; 0, -40]
      DstBlock		      "Display"
      DstPort		      1
    }
    Line {
      ZOrder		      3
      SrcBlock		      "Complex to\nMagnitude-Angle"
      SrcPort		      2
      Points		      [75, 0; 0, 65]
      DstBlock		      "Display1"
      DstPort		      1
    }""")

m.update_blk_info("""   Block {
      BlockType		      SignalGenerator
      Name		      "X1"
      SID		      9
      Ports		      [0, 1]
      Position		      [15, 55, 45, 85]
      WaveForm		      "square"
      Frequency		      ".4"
    }
    Block {
      BlockType		      SignalGenerator
      Name		      "X2"
      SID		      10
      Ports		      [0, 1]
      Position		      [15, 105, 45, 135]
      WaveForm		      "square"
      Frequency		      ".2"
    }""")

m.get_src_dst()'''