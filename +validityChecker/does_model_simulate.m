function simulates = does_model_simulate(model)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
            try
                sim(model);
                simulates = 1;
            catch ME 
               
                disp(['ERROR ID : ' ME.identifier]);
                disp(['ERROR MSG : ' ME.message]);

                simulates = 0;
            end
end

