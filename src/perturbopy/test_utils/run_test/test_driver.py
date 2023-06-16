"""
   Run an executable for the testsuite.
"""
import os
import sys
import shlex
import shutil
import subprocess
from perturbopy.io_utils.io import open_yaml
from perturbopy.test_utils.run_test.env_utils import perturbo_run_from_env
from perturbopy.test_utils.run_test.env_utils import perturbo_scratch_dir_from_env
from perturbopy.test_utils.run_test.run_utils import print_test_info
from perturbopy.test_utils.run_test.run_utils import setup_default_tol


def run_perturbo(cwd, perturbo_driver_dir_path,
                 input_name='pert.in', output_name='pert.out'):
    """
    Function to run Perturbo and produce output files

    .. note ::
       The Perturbo run command must be specified in the PERTURBO_RUN environment
       variable. Check the perturbopy/tests/test_scripts/env_setup_examples.sh script
       for examples.


    Parameters
    ----------
    cwd : str
       path of current working directory
    perturbo_driver_dir_path : str
       path to dir with pert.in file
    input_name : str, optional
       name of the input file, default: 'pert.in'
    output_name : str, optional
       name of the output file, default: 'pert.out'

    Returns
    -------
    None

    """

    perturbo_run = perturbo_run_from_env()

    perturbo_run = f'{perturbo_run} -i {input_name} | tee {output_name}'

    os.chdir(perturbo_driver_dir_path)

    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')

    print(f' === Running Perturbo === :\n {perturbo_run}')
    sys.stdout.flush()

    subprocess.run(shlex.split(perturbo_run))

    os.chdir(cwd)
    
def run_scf(cwd, work_path, input_yaml, input_name='scf.in', output_name='scf.out'):
    """
    Function for scf calculation

    Parameters
    ----------
    cwd : str
       path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    input_yaml : dict
        dictionary, which include the
    commands for scf calculation
    input_name : str, optional
       name of the input file, default: 'scf.in'
    output_name : str, optional
       name of the output file, default: 'scf.out'

    Returns
    -------
    None

    """

    command = input_yaml['comp_info']['scf']
    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(f'{work_path}/pw-ph-wann/scf/')

    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')

    print(f' === Running scf === :\n {run}')
    sys.stdout.flush()

    full_run = 'module load qe\n' + run 
    subprocess.run(full_run, shell=True)

    os.chdir(cwd)
    
def run_phonon(cwd, work_path, input_yaml, input_name='ph.in', output_name='ph.out'):
    """
    Function for nscf calculation

    Parameters
    ----------
    cwd : str
       path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    input_yaml : dict
        dictionary, which include the
    commands for phonon calculation
    input_name : str, optional
       name of the input file, default: 'ph.in'
    output_name : str, optional
       name of the output file, default: 'ph.out'

    Returns
    -------
    None

    """

    command = input_yaml['comp_info']['phonon']
    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(f'{work_path}/pw-ph-wann/phonon/')
    #softlink = 'ln -sf ../scf/tmp'
    softlink = '../scf/tmp'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from scf= :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, 'tmp')
    #subprocess.run(shlex.split(softlink))

    print(f' == Running Phonon = :\n {run}')
    sys.stdout.flush()

    full_run = 'module load qe\n' + run 
    subprocess.run(full_run, shell=True)
    
    collect = 'bash ./ph-collect.sh'
    print(f' == Collect files == :\n {collect}')
    sys.stdout.flush()
    
    subprocess.run(shlex.split(collect))
    

    os.chdir(cwd)

    
def run_nscf(cwd, work_path, input_yaml, input_name='nscf.in', output_name='nscf.out'):
    """
    Function for nscf calculation

    Parameters
    ----------
    cwd : str
       path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    input_yaml : dict
        dictionary, which include the
    commands for nscf calculation
    input_name : str, optional
       name of the input file, default: 'nscf.in'
    output_name : str, optional
       name of the output file, default: 'nscf.out'

    Returns
    -------
    None

    """

    command = input_yaml['comp_info']['nscf']
    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(f'{work_path}/pw-ph-wann/nscf/')
    #softlink = 'ln -sf ../scf/tmp'
    softlink = '../scf/tmp'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from scf= :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, 'tmp')
    #subprocess.run(shlex.split(softlink))

    print(f' === Running nscf === :\n {run}')
    sys.stdout.flush()

    full_run = 'module load qe\n' + run 
    subprocess.run(full_run, shell=True)

    os.chdir(cwd)
    
def run_wannier(cwd, work_path, input_yaml, ephr_name, input_name='pw2wan.in', output_name='pw2wan.out'):
    """
    Function for wannier90 calculation

    Parameters
    ----------
    cwd : str
       path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    input_yaml : dict
        dictionary, which include the
    commands for wannier calculation
    ephr_name : str
        name of the running calculation
    input_name : str, optional
       name of the input file, default: 'pw2wan.in'
    output_name : str, optional
       name of the output file, default: 'pw2wan.out'

    Returns
    -------
    None

    """

    command = input_yaml['comp_info']['wannier']['wannier90']
    prefix = input_yaml['prefix'][ephr_name]
    run = f'{command} -pp {prefix}'
    
    # link the save-file from scf calculation
    os.chdir(f'{work_path}/pw-ph-wann/wann/')
    os.mkdir('tmp')
    #os.chdir('tmp/')
    #softlink = f'ln -sf ../../scf/tmp/{prefix}.save'
    softlink = f'../../scf/tmp/{prefix}.save'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from scf= :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, f'tmp/{prefix}.save')
    #subprocess.run(shlex.split(softlink))

    #os.chdir('..')
    # first run of wannier90
    print(f' === Running pp === :\n {run}')
    sys.stdout.flush()
    full_run = 'module load qe\n' + run 
    subprocess.run(full_run, shell=True)
    
    # run of pw2wan
    command = input_yaml['comp_info']['wannier']['pw2wannier90']
    run = f'{command} -i {input_name} | tee {output_name}'
    print(f' = Running pw2wan = :\n {run}')
    sys.stdout.flush()
    full_run = 'module load qe\n' + run 
    subprocess.run(full_run, shell=True)
    
    # second run of wannier90
    command = input_yaml['comp_info']['wannier']['wannier90']
    run = f'{command} {prefix}'
    print(f' = Running Wannier= :\n {run}')
    sys.stdout.flush()
    full_run = 'module load qe\n' + run 
    subprocess.run(full_run, shell=True)
    
    os.chdir(cwd)
    
def run_qe2pert(cwd, work_path, input_yaml, ephr_name, input_name='qe2pert.in', output_name='qe2pert.out'):
    """
    Function for qe2pert calculation

    Parameters
    ----------
    cwd : str
       path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    input_yaml : dict
        dictionary, which include the
    commands for qe2pert calculation
    ephr_name : str
        name of the running calculation
    input_name : str, optional
       name of the input file, default: 'qe2pert.in'
    output_name : str, optional
       name of the output file, default: 'qe2pert.out'

    Returns
    -------
    None

    """

    command = input_yaml['comp_info']['qe2pert']
    prefix = input_yaml['prefix'][ephr_name]
    run = f'{command} -i {input_name} | tee {output_name}'

    # link the save-file from scf calculation
    os.chdir(f'{work_path}/qe2pert/')
    os.mkdir('tmp')
    #os.chdir('tmp/')
    #softlink = f'ln -sf ../../pw-ph-wann/nscf/tmp/{prefix}.save'
    softlink = f'../../pw-ph-wann/nscf/tmp/{prefix}.save'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from nscf :\n {softlink}')
    sys.stdout.flush()
    #subprocess.run(shlex.split(softlink))
    #os.chdir('..')
    os.symlink(softlink, f'tmp/{prefix}.save')
    
    # link rest files
    #softlink = f'ln -sf ../pw-ph-wann/wann/{prefix}_u.mat'
    softlink = f'../pw-ph-wann/wann/{prefix}_u.mat'
    print(f'\n = Link rest files = :\n {softlink};')
    sys.stdout.flush()
    #subprocess.run(shlex.split(softlink))
    os.symlink(softlink, f'{prefix}_u.mat')
    #softlink = f'ln -sf ../pw-ph-wann/wann/{prefix}_u_dis.mat'
    softlink = f'../pw-ph-wann/wann/{prefix}_u_dis.mat'
    print(f'\n {softlink};')
    sys.stdout.flush()
    #subprocess.run(shlex.split(softlink))
    os.symlink(softlink, f'{prefix}_u_dis.mat')
    #softlink = f'ln -sf ../pw-ph-wann/wann/{prefix}_centres.xyz'
    softlink = f'../pw-ph-wann/wann/{prefix}_centres.xyz'
    print(f'\n {softlink};')
    sys.stdout.flush()
    os.symlink(softlink, f'{prefix}_centres.xyz')
    #subprocess.run(shlex.split(softlink))


    # run qe2pert
    print(f' = Running qe2pert = :\n {run}')
    sys.stdout.flush()
    full_run = 'module load perturbo\n' + run 
    subprocess.run(full_run, shell=True)

    os.chdir(cwd)

def get_test_materials(test_name):
    """
    Run one test:
       #. run perturbo.x to produce output files
       #. determine paths to files for comparison
       #. associated settings for file comparison with file paths

    Parameters
    ----------
    test_name : str
       name of test

    Returns
    -----
    ref_outs : list
       list of paths to reference files
    new_outs : list
       list of paths to outputted files
    igns_n_tols : list
       list of dictionaries containing the ignore keywords and tolerances needed to performance comparison of ref_outs and new_outs

    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = 'tests_perturbo/' + test_name
    ref_data_path_suffix = 'refs_perturbo/' + test_name

    cwd = os.getcwd()

    # determine needed paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_from_env(cwd, perturbo_inputs_dir_path, test_name)
    ref_path                 = [x[0] for x in os.walk(cwd) if x[0].endswith(ref_data_path_suffix)][0]

    # input yaml for perturbo job
    pert_input = open_yaml(f'{work_path}/pert_input.yml')
    # dictionary containing information about files to check
    test_files = pert_input['test info']['test files']
    # names of files to check
    out_files  = test_files.keys()
    # list of full paths to reference outputs
    ref_outs    = [ref_path + '/' + out_file for out_file in out_files]
    # list of full paths to new outputs
    new_outs    = [work_path + '/' + out_file for out_file in out_files]

    # remove outputs if they already exist
    # WARNING: the output files can sometimes serve as inputs
    # for out_file in new_outs:
    #    if os.path.exists(out_file):
    #       os.remove(out_file)

    # print the test information before the run
    print_test_info(test_name, pert_input)

    # run Perturbo to produce outputs
    run_perturbo(cwd, work_path)

    # list of dict. Each dict contains ignore keywords and
    # tolerances (information about how to compare outputs)
    igns_n_tols = [test_files[out_file] for out_file in out_files]

    igns_n_tols = setup_default_tol(igns_n_tols)

    return (ref_outs,
            new_outs,
            igns_n_tols)


def run_ephr_calculation(ephr_name):
    """
    Run one test:
        #. Run scf calculation
        #. Run phonon calculation
        #. Run nscf calculation
        #. Run wannier90 calculation
        #. Run qe2pert calculation

    Parameters
    ----------
    ephr_name : str
        name of computed ephr_name file

    Returns
    -----
    None
    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = f'ephr_computation/{ephr_name}'

    cwd = os.getcwd()

    # determine needed paths
    inputs_dir_path = f'{cwd}/{inputs_path_suffix}/'
    work_path = perturbo_scratch_dir_from_env(cwd, inputs_dir_path, ephr_name)
    
    # input yaml for the whole qe2pert calculation
    yaml_prefix = cwd
    input_yaml = open_yaml(f'{yaml_prefix}/ephr_computation/qe2pert_input.yml')

    # print the test information before the run
    print_test_info(ephr_name, input_yaml)

    # run scf
    run_scf(cwd, work_path, input_yaml)
    
    # run phonon
    run_phonon(cwd, work_path, input_yaml)

    # run nscf
    run_nscf(cwd, work_path, input_yaml)
    
    # run wannier90
    run_wannier(cwd, work_path, input_yaml, ephr_name)
    
    # run qe2pert
    run_qe2pert(cwd, work_path, input_yaml, ephr_name)

    return

def clean_test_materials(test_name, new_outs):
    """
    clean one test:
       #. removes new files and dirs produced by test

    Parameters
    ----------
    test_name : str
       name of test
    new_outs : list
       list of paths to produced outputs

    Returns
    -----
    None

    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = 'tests_perturbo/' + test_name

    cwd = os.getcwd()

    # determine paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_from_env(cwd, perturbo_inputs_dir_path, test_name, rm_preexist_dir=False)

    if os.path.isdir(work_path):
        print(f'\n === Test {test_name} passed ===\n\n Removing {work_path} ...')
        shutil.rmtree(work_path)

    return None
