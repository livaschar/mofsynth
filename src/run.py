from __utils__ import synth_eval, results, check_opt

'''TO RUN THE SYNTH EVALUATION'''
# directory = 'cifs_1'
# cifs, linkers, fault_fragmentation, fault_smiles = synth_eval(directory) # Lists with the cifs found in the directory and all the linkers. print(cifs[0].name), print(linkers[0].smiles)

''' CHECK ONLY TO SEE WHICH CONVERGED '''
# converged, not_converged = check_opt()

# with open('converged.txt', 'w') as f:
#     for i in converged:
#         f.write(f"{i.smiles} {i.mof_name}\n")
    
# with open('not_converged.txt', 'w') as f:
#     for i in not_converged:
#         f.write(f"{i.smiles} {i.mof_name}\n")

'''If runs have finished'''
txt_path = results()


exit()
''' Utilities for further thinking'''

'''FIND A SPECIFIC MOF FROM THE LIST OF CIFS'''
def find_object_by_name(name, object_list):
    for obj in object_list:
        if obj.name == name:
            return obj
    return None  # Return None if the object with the specified name is not found

# Example usage
desired_name = "Object2"
found_object = find_object_by_name(desired_name, objects_list)

if found_object:
    print(f"Object found: {found_object.name}")
    # Access other attributes if needed, e.g., found_object.smiles
else:
    print(f"No object found with name '{desired_name}'.")
'''------------------------------------------'''