function compiles = does_model_compile(model)
            Error= containers.Map;
            try
                slreportgen.utils.compileModel(model)
                compiles = slreportgen.utils.isModelCompiled(model);
                if compiles  
                    slreportgen.utils.uncompileModel(model);
                     
                end 
               
                %eval([model, '([], [], [], ''compile'');']);
                %compiles = 0;
            catch ME 
                if ~isKey(Error,ME.identifier)
                    Error(ME.identifier) =1;
                else
                    Error(ME.identifier) =Error(ME.identifier) +1;
                end
                disp(['ERROR ID : ' ME.identifier]);
                disp(['ERROR MSG : ' ME.message]);

                compiles = 0;
            end
end