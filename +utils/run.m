function run(directory,filename)
%UNTITLED9 Summary of this function goes here
%   Detailed explanation goes here
    [model_files] = dir(directory);
    tf = ismember( {model_files.name}, {'.', '..'});
    model_files(tf) = [];  %remove current and parent directory.
    blk_lib_map = utils.getblock_library_map();
    for cnt = 1:numel(model_files)
        fprintf('Processing %d\n',cnt);
        file = strcat(directory,filesep,model_files(cnt).name);
        try
            ret = utils.get_adjList(file,blk_lib_map);
        catch
            continue    
        end
        utils.write_adj_list(ret,'Write',filename);
    
    end
    utils.write_adj_list('', 'Close',filename);  

end

