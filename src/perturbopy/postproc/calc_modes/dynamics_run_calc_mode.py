import numpy as np
import os
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.calc_modes.dynamics_run import DynamicsRun
from perturbopy.io_utils.io import open_yaml, open_hdf5, close_hdf5

class DynamicsRunCalcMode(CalcMode):
    """
    Class representation of a Perturbo dynamics-run calculation.

    Parameters
    ----------
    pert_dict : dict
        Dictionary containing the inputs and outputs from the transport calculation.

    """

    def __init__(self, cdyna_file, tet_file pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'dynamics-run':
            raise ValueError('Calculation mode for a DynamicsRunCalcMode object should be "dynamics-run"')

        self._dat = {}
        self.time_units = 'fs'

        num_runs = cdyna_file['num_runs'][()]

        for irun in range(1, num_runs + 1):
            dyn_str = f'dynamics_run_{irun}'

            num_steps = cdyna_file[dyn_str]['num_steps'][()]
            time_step = cdyna_file[dyn_str]['time_step_fs'][()]

            # a dynamics run must have at least one snap
            numk, numb = cdyna_file[dyn_str]['snap_t_1'][()].shape

            snap_t = np.zeros((numb, numk, num_steps), dtype=np.float64)

            for itime in range(num_steps):
                snap_t[:, :, itime] = cdyna_file[dyn_str][f'snap_t_{itime+1}'][()].T

            # Get E-field, which is only present if nonzero
            if "efield" in cdyna_file[dyn_str].keys():
                efield = cdyna_file[dyn_str]["efield"][()]
            else: 
                efield = np.array([0.0, 0.0, 0.0])

            self._dat[irun] = DynamicsRun(num_steps, time_step, snap_t, efield)


    @classmethod
    def from_hdf5_yaml(cls, cdyna_path, tet_path, yaml_path='pert_output.yml'):
        """
        Class method to create a DynamicsRunCalcMode object from the HDF5 file and YAML file
        generated by a Perturbo calculation

        Parameters
        ----------
        yaml_path : str
           Path to the HDF5 file generated by a dynamics-run calculation
        yaml_path : str, optional
           Path to the YAML file generated by a dynamics-run calculation

        Returns
        -------
        dyanamics_run : DynamicsRunCalcMode
           The DynamicsRunCalcMode object generated from the HDF5 and YAML files

        """

        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')
        if not os.path.isfile(cdyna_path):
            raise FileNotFoundError(f'File {cdyna_path} not found')
        if not os.path.isfile(tet_path):
            raise FileNotFoundError(f'File {tet_path} not found')

        yaml_dict = open_yaml(yaml_path)
        cdyna_file = open_hdf5(cdyna_path)
        tet_file = open_hdf5(tet_path)

        return cls(cdyna_file, tet_file, yaml_dict)


    def __getitem__(self, index):
        """
        Method to index the DynamicsRunCalcMode object

        Parameters
        ----------
        index : int
            The dynamics run requested

        Returns
        -------
        dynamics_run: DynamicsRun
           Object containing information for the dynamics run

        """
        return self._dat[index]
