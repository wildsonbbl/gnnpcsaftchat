"helper for plotting"

import numpy as np
from gnnepcsaft.epcsaft.epcsaft_feos import pure_den_feos
from gnnepcsaft_mcp_server.utils import predict_epcsaft_parameters


def plot_pure_density(smiles: str, t_min: float, t_max: float, pressure: float):
    """
    When asked, use this tool to show the user a plot of density.
    Answer the user with the exact result of this tool to show the plot.

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

    return f"""
<div id="den_plot" alt="Density plot"></div>
<script>
var rho_data = {data};
getplot(rho_data,0,"Liquid Density (mol/m³)","den_plot");
</script>
"""
