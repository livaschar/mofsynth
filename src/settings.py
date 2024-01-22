def settings_from_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
    job_sh = lines[0].split()[1:]
    run_str = lines[1].split()[1:]
    cycles = lines[2].split()[1:]
    return run_str, job_sh, cycles

def user_settings():
    run_str = input("\nProvide the string with which the optimization program runs: ")

    question = input("\nIs there a file in MOFSynth/Files folder that is necessary to run your optimization programm? [y/n]: ")
    if question == 'y':
        job_sh = input("\nSpecify the file name: ")
    else:
        job_sh = None
    
    cycles = input("\nPlease specify the number of optimization cycles (default = 1000): ")
    try:
        cycles = int(cycles)
    except:
        print("Not a valid value provided. Default value will be used")
        cycles = '1000'
    
    return run_str, job_sh, cycles