function loaded = does_model_load(model)
            try
               load_system(model)
               
                close_system(model);
               loaded = 1;
           catch ME 
            
                loaded = 0;
            end
end