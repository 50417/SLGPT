function [blocktype_lib_map] = getblock_library_map()
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
blocktype_lib_map = containers.Map();
load_system('simulink');;
%x = find_system('simulink', 'LookUnderMasks', 'all', 'Type', 'Block');
%get_param(x,'BlockType')
simulinkLibraryPaths = find_system('simulink', 'Type', 'Block');
simulinkLibraryBlockTypes = get_param(simulinkLibraryPaths, 'BlockType');
    for n = 1 : numel(simulinkLibraryPaths)
        k = simulinkLibraryBlockTypes{n};
        if(~isKey(blocktype_lib_map,k))
  
             blocktype_lib_map(k) = {};
           
        end
        val =  blocktype_lib_map(k); 
        val{end+1} = simulinkLibraryPaths{n};
         blocktype_lib_map(k) = val;
    
    end
end

