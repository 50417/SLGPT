import networkx as nx
from Graph_Info import Graph_Info
from math import isinf
import numpy as np
import os
import json
def calculate_graph_metric( using_json=False,simulink_name=None, adjList=None, source=None, sinks=None, blocks=None):
    import json
    DG = nx.DiGraph()
    gi = Graph_Info(simulink_name)
    if not using_json:
        #Deprecated. TODO : Add this feature
        tmp_output, model_info = extract_system_blk()

        for nodes in model_info.blk_info.keys():
            DG.add_node(nodes)
        for blk in model_info.graph.keys():

            for tup in model_info.graph[blk]:
                dst_lst = tup[0]
                for dst in dst_lst:
                    DG.add_edge(blk, dst)
    else:
        for nodes in blocks:
            DG.add_node(nodes)

        for src, dst in adjList.items():
            for d in dst:
                # print(src)
                DG.add_edge(src, d)

    # import matplotlib.pyplot as plt
    # nx.draw(DG,with_labels=True, font_weight='bold')
    # plt.show()
    '''
    source =[]
    dst = []
    for node, deg in DG.in_degree():
        if(deg==0):
            source.append(node)

    for node, deg in DG.out_degree():
        if(deg==0):
            dst.append(node)
    #print(dst)
    '''

    for src in source:

        for d in sinks:

            for path in nx.all_simple_paths(DG, src, d):
                gi.addpath(path)

                # print(path)

    UG = DG.to_undirected()
    sub_graphs = nx.connected_components(UG)

    for c in sub_graphs:
        gi.add_subgraph(list(c))
        # print(c)
    gi.add_subgraph([])
    gi.subgraphs_size.sort()

    return gi  # json.dumps(gi.__dict__)

def run(model_name,train_data,dir,dbfile):
    saveImageIn ='../Experiments/Plots'
    if not os.path.isdir(saveImageIn):
        os.makedirs(saveImageIn)
    ans = []
    file= 'adjList-'+model_name+'From'+train_data+'Compiled.json'
    inputfile = os.path.join(dir,file)

    with open(inputfile) as f:
            dict = json.load(f)
            for d in dict:
                #print(d['adjList'])
                ans.append(calculate_graph_metric(True,d['simulink_name'], d['adjList'],d['sources'],d['sinks'],d['blocks']))



    outputfile = 'test.json'
    with open(outputfile, 'w', encoding='utf') as f:
        f.write('[')
        for k in range(len(ans)-1):
            f.write(json.dumps(ans[k].__dict__,indent=4)+",\n")
        f.write(json.dumps(ans[len(ans)-1].__dict__, indent=4) + "\n")
        f.write(']')


    ans = []
    counter = 0
    no_of_subgraphs = []
    source_destination_path = []
    max_source_destination_path_length = []
    min_source_destination_path_length = []
    max_sub_graph_size = []
    x = []
    with open(outputfile) as f:
            dict = json.load(f)

            for d in dict:
                x.append(counter)
                counter += 1
                no_of_subgraphs.append(d['no_of_subgraphs'])
                source_destination_path.append(d['source_destination_path'])
                max_source_destination_path_length.append(d['max_source_destination_path_length'])
                max_sub_graph_size.append(d['max_sub_graph_size'])
                if isinf(d['min_source_destination_path_length']):
                    min_source_destination_path_length.append(0)
                else:
                    min_source_destination_path_length.append(d['min_source_destination_path_length'])
                #print(d['adjList'])
                #ans.append(processor.calculate_graph_metric(True, d['adjList']))
            no_of_subgraphs.sort()
            source_destination_path.sort()
            max_source_destination_path_length.sort()
            min_source_destination_path_length.sort()
            max_sub_graph_size.sort()

    from sqlalchemy import create_engine
    from sqlalchemy.sql import text


    engine = create_engine('sqlite:///'+dbfile, echo=True) 
    blk_count = []
    conn_count = []
    with engine.connect() as con:

        statement = text("Select SCHK_Block_count from "+model_name+"_From_"+train_data+"_Metric") 
        st2 = text("Select total_connH_cnt from "+model_name+"_From_"+train_data+"_Metric")

        r2 =  con.execute(st2)
        result  =  con.execute(statement)
        for row in result:
            for key, val in row.items():

                blk_count.append(val)
        for row in r2:
            for key, val in row.items():
                conn_count.append(val)

    blk_count.sort()
    conn_count.sort()
    import matplotlib.ticker as mtick
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 18})

    plt.plot(x,no_of_subgraphs, color="black")
    plt.xticks(np.linspace(1,len(no_of_subgraphs),5), ('0%', '20%', '40%', '60%', '100%'))
    ax = plt.gca()
    plt.text(0.15, 0.9, 'N='+str(len(x)), ha='center', va='center', transform=ax.transAxes, style='italic'   )
    plt.savefig(os.path.join(saveImageIn,model_name+"_From_"+train_data+"_no_of_subgraphs.png"))
    plt.close()

    plt.plot(x,max_sub_graph_size,color="black")
    plt.xticks(np.linspace(1,len(no_of_subgraphs),5), ('0%', '20%', '40%', '60%', '100%'))
    ax = plt.gca()
    plt.text(0.15, 0.9, 'N='+str(len(x)), ha='center', va='center', transform=ax.transAxes, style='italic'   )
    plt.savefig(os.path.join(saveImageIn,model_name+"_From_"+train_data+"_max_sub_graph_size.png"))
    plt.close()

    plt.plot(max_source_destination_path_length,color="black")
    plt.xticks(np.linspace(1,len(no_of_subgraphs),5), ('0%', '20%', '40%', '60%', '100%'))
    import matplotlib.ticker as ticker
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax = plt.gca()
    plt.text(0.15, 0.9, 'N='+str(len(x)), ha='center', va='center', transform=ax.transAxes, style='italic'   )
    plt.savefig(os.path.join(saveImageIn,model_name+"_From_"+train_data+"_max_source_destination_path_length.png"))
    plt.close()

    plt.plot(conn_count,color="black")
    plt.xticks(np.linspace(1,len(conn_count),5), ('0%', '20%', '40%', '60%', '100%'))
    ax = plt.gca()
    plt.text(0.15, 0.9, 'N='+str(len(x)), ha='center', va='center', transform=ax.transAxes, style='italic'   )
    plt.savefig(os.path.join(saveImageIn,model_name+"_From_"+train_data+"_conn_count.png"))
    plt.close()

    plt.plot(x,blk_count,color="black")
    plt.xticks(np.linspace(1,len(blk_count),5), ('0%', '20%', '40%', '60%', '100%'))
    ax = plt.gca()
    plt.text(0.15, 0.9, 'N='+str(len(x)), ha='center', va='center', transform=ax.transAxes, style='italic'   )
    plt.savefig(os.path.join(saveImageIn,model_name+"_From_"+train_data+"_blk_count.png"))
    plt.close()
models = ["DeepFuzzSL","SLGPT","RealWorld","SLforge"]
data_source = ["RealWorld","SLforge"]

dir = ''
dbfile = ""

for data in data_source:
    for model in models:
        try:
            run(model,data,dir,dbfile)
        except Exception as e:
            continue
