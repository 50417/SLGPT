import re
def get_tokens(line):
    '''
    This functions returns key value pair of Simulink separated by first whitespace
    args:
        line: any text
        returns:
            two element list separated from the first white space.
    '''
    line = remove_extra_white_spaces(line)
    return line.split(" ",1)

def remove_extra_white_spaces(line):
    '''
    removes extra white spaces in the text
    and converts to lowercase.
    args:
        line: any text
        returns:
            a text with no duplicate whitespace
    '''
    line = line.strip()
    line = re.sub('\t', ' ', line)
    line = re.sub(' +', ' ', line)
    return line



def blk_name_check(name):#= '"Complexko\"'):
    '''
        varibles name or block name rules in Simulink are recommended but not enforced . So blk name can be multi-line with quotes in their name.
        This functions checks if block we have seen so far is complete block name. For example : "Complex\n number". So a Block name is not the name between quotes only.
        TODO: Doesnot handle the case when there is \" in the name.
    '''
    stack = []
    prev = ''
    #print(repr(name).encode('unicode_escape'))
    #print(name)

    for char in name:
        #print(char)
        if char == '"':
            #print(prev)
            if len(stack)==0 or prev == '\\':
                stack.append('"')
            else:
                stack.pop()
        prev = char
    #print(stack)
    if len(stack) == 0:
        return True
    else:
        return False

#print(blk_name_check())