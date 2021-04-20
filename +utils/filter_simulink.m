function filter_simulink(directory)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
%{
m = getblock_library_map();
 k = keys(m);
 counter = 0
for n = 1 : numel(k)
val = m(k{n});
[r,c] = size(val);
  for f = 1:c
      lib = regexprep(val{f}, '[\n\r]+',' ');
      if(contains(lib,"simulink/Sources"))
          disp(k{n});
          counter = counter + 1;
          fprintf("%d : %s\n ",f,regexprep(val{f}, '[\n\r]+',' '));
          
      end
      
  end
 
    %{
if(c>1)
    counter = counter +1;
    fprintf("%d: %s\n",n,k{n});
    for f = 1:c
        fprintf("%d : %s\n ",f,regexprep(val{f}, '[\n\r]+',' '));
    end
    disp("+========================")

end
%}

end

 disp("====")
counter
%}

 [model_files] = dir(directory);
    tf = ismember( {model_files.name}, {'.', '..'});
    model_files(tf) = [];  %remove current and parent directory.
    counter = 0 ;
    
        saveToDir = ['Experiments' filesep 'filtered'];
 if ~exist(saveToDir, 'dir')
        mkdir(saveToDir);
 end
for cnt = 1:numel(model_files)
    model = [directory filesep model_files(cnt).name];
    fprintf('Processing %s\n',model_files(cnt).name);
    [names,~] = dependencies.toolboxDependencyAnalysis({model});
    noOfToolBoxes = numel(names);
    if ~isempty(find(strcmp(names,'Simulink'), 1))
        if noOfToolBoxes==1 || (noOfToolBoxes==2 && ~isempty(find(strcmp(names,'MATLAB'), 1)))
            load_system(model);
            sf_charts = find_system(gcs,'MaskType','Stateflow');
            unresolvedlibLinks = find_system(gcs,'LinkStatus','unresolved');
            close_system(model);
            if (isempty(sf_charts) && isempty(unresolvedlibLinks))
                copyfile(model,saveToDir);
                counter = counter + 1;
            end
            %fprintf("%s \n ==================")
        end
    end

     fprintf('Complete Processing %s\n==================',model_files(cnt).name);

end
        
  
end


