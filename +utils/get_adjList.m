function ret = get_adjList(model,blk_lib_map)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
    load_system(model);
    ret.modelname = gcs;
    
    % all Blocks:
    blks = find_system(gcs,'SearchDepth',1);
    blks = blks(2:end);
    
   
    
    ret.adjList = containers.Map;
    
    no_of_unique_blks = numel(blks);
    blk_name_list =   cell(no_of_unique_blks,1);
    blk_name_list(:) = {''}; %pre allocating cell array of char type
    
    for c = 1: no_of_unique_blks
        blk_name_list{c} = get_param(blks{c},'Name');
    end
    ret.blks = blk_name_list;
    sources = {};
    sinks = {};
    
    %getting connections for each blk
    for(cnt = 1:no_of_unique_blks)
        src = get_param(blks{cnt},'Name');
        ports_info = get_param(blks{cnt},'PortConnectivity'); 
        block_type = get_param(blks{cnt}, 'BlockType');
        if(strcmp(block_type,'Scope'))
                sinks{end+1} = src;
        else
            if sum(size(ports_info)) <= 2 && ~(strcmp(block_type,'From') || strcmp(block_type,'Goto'))
                if(strcmp(block_type,'Scope') || any(size(ports_info.SrcBlock))) % Floating Scope
                    sinks{end+1} = src;
                elseif (any(size(ports_info.DstBlock)))
                    sources{end+1} = src;
                end 
            end
        end
        %{
        block_lib  = blk_lib_map(block_type);
        [r,c] = size(block_lib);
        for q = 1:c
            lib = block_lib{q};
            if(contains(lib,"simulink/Sources"))
                sources{end+1} = src;
            end 
            if (contains(lib,"simulink/Sinks"))
                sinks{end+1} = src;
            end
        end
        %}
        connected_blks = get_param(blks{cnt},'PortConnectivity');
        n= numel(connected_blks); %numbers of blocks connected to this blk
        for k=1:n
            n_dst = numel(connected_blks(k).DstBlock);
            list_of_dst =  cell(n_dst,1);
            list_of_dst(:) = {''}; %pre allocating cell array of char type
            for d = 1: n_dst

                dst = get(connected_blks(k).DstBlock(d));
                list_of_dst{d} = dst.Name;
            end
           ret.adjList(src) = list_of_dst;
  
        end
    end
    ret.sources = unique(sources); 
    ret.sinks = unique(sinks);
    
   
    
    close_system(model);
    
end

