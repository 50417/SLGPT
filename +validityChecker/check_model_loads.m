sys = ''
[list_of_files] = dir(sys)
tf = ismember( {list_of_files.name}, {'.', '..'});
list_of_files(tf) = [];  %remove current and parent directory.
rocessed_file_count = 1;
%Loop over each Zip File 
error_models = 0 ;
err = [""];
    lst = [" "];
for cnt = 1 : size(list_of_files) 
    name =strtrim(char(list_of_files(cnt).name)) ;
    model_name = strrep(name,'.slx','');
    model_name = strrep(model_name,'.mdl','');
    try
        load_system([sys filesep name])
    catch ME
        err(end+1) = model_name;
        
        continue
    end

end
