function write_adj_list(ret,cmd,filename)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
working_dir = ['Experiments' filesep 'adjList'];
 if ~exist(working_dir, 'dir')
        mkdir(working_dir);
 end
 filename = [working_dir filesep filename];
if(strcmp(cmd,'Close'))
    FID = fopen(filename, 'a+');
    fprintf( FID,'%s\n',']');
    return;
end
  
    k = keys(ret.adjList);
    FID = -1;
  if(~isfile(filename))
    FID = fopen(filename, 'a+');
    fprintf( FID,'%s\n','[');
  else
       FID = fopen(filename, 'a+');
      fprintf(FID, '%s\n',',');
  end
      if FID < 0
         error('Cannot open file');
      end
      s = struct("simulink_name", ret.modelname, "blocks",{ret.blks},"sources", {ret.sources}, "sinks", {ret.sinks}, "adjList", {ret.adjList});
      encodedJSON = jsonencode(s);
      fprintf(FID,strrep(encodedJSON, '\', '\\'));
      
      %Printing
      %{
    for m = 1: numel(k)
        i =   ret.adjList(k{m});
        for d = 1:numel(ret.adjList(k{m}))
        
          fprintf( '%s:%s:%s\n',ret.modelname, k{m},i{d});
        end
    end 
    %}
    fclose(FID);
    FID = -1;
   
           
end

