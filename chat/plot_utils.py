"helper for plotting"

import uuid

import numpy as np
from gnnepcsaft.epcsaft.epcsaft_feos import pure_den_feos
from gnnepcsaft_mcp_server.utils import predict_epcsaft_parameters


def plot_pure_density(smiles: str, t_min: float, t_max: float, pressure: float):
    """
    When asked, use this tool to show the user a plot of density.
    To show the plot, answer the user with the exact content from
    the result part of this tool.

    Args:
      smiles (str): SMILES of the molecule.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)

    """

    temperatures = np.linspace(t_min, t_max, 20, dtype=np.float64)
    parameters = predict_epcsaft_parameters(smiles)

    densities = [
        pure_den_feos(parameters=parameters, state=[T, pressure]) for T in temperatures
    ]

    data = [[temperatures.tolist(), densities], [[], []]]
    plot_id = f"den_plot_{uuid.uuid4().hex}"

    return f"""
    <div class="col-lg">
    <div id="{plot_id}" alt="Density plot"></div>
    <script>
    getplot({data},0,"Liquid Density (mol/m³)","{plot_id}");
    </script>
    </div>
    """
