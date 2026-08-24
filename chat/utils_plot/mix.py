"helper for plotting mixtures"

import json
import uuid
from typing import Dict, List, Optional

import numpy as np
from gnnepcsaft_mcp_server.utils_data import (
    retrieve_bubble_pressure_data,
    retrieve_lle_binary_data,
    retrieve_lle_ternary_data,
    retrieve_rho_binary_data,
    retrieve_rho_ternary_data,
    retrieve_vle_binary_data,
    retrieve_vle_pxy_binary_data,
    retrieve_vle_ternary_data,
    retrieve_vle_ternary_tx_fixed_data,
)
from gnnepcsaft_mcp_server.utils_mix import (
    MixDenParams,
    MixLLEParams,
    MixVpParams,
    TernaryVleTxParams,
    mix_den,
    mix_lle,
    mix_ternary_lle,
    mix_ternary_vle_tx_fixed,
    mix_vle,
    mix_vle_pxy,
    mix_vp,
)

from .core import PA_PER_KPA, _experimental_plot_data, _make_plot_response

PLOT_HTML_STORE: Dict[str, str] = {}
PA_PER_KPA = 1000.0
MN_PER_N = 1000.0


def plot_mix_density(  # pylint: disable=R0913,R0917
    smiles_list: List[str],
    t_min: float,
    t_max: float,
    pressure: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a plot of density (mol/m³) for a mixture.

    Args:
      smiles_list (List[str]): List of mixture SMILES.
      t_min (float): minimum temperature (K) to calculate density (mol/m³)
      t_max (float): maximun temperature (K) to calculate density (mol/m³)
      pressure (float): system pressure (Pa)
      mole_fractions (List[float]): mole fractions list
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, mix_densities = mix_den(
        MixDenParams(
            smiles_list=smiles_list,
            mole_fractions=mole_fractions,
            kij_matrix=kij_matrix if kij_matrix else [],
            min_temp=t_min,
            max_temp=t_max,
            pressure=pressure,
            npoints=npoints,
        )
    )

    if len(smiles_list) == 2:
        exp_data = retrieve_rho_binary_data(
            smiles_list=smiles_list,
            pressure=pressure / PA_PER_KPA,
            x1=mole_fractions[0],
        )
    elif len(smiles_list) == 3:
        exp_data = retrieve_rho_ternary_data(
            smiles_list=smiles_list,
            pressure=pressure / PA_PER_KPA,
            x1=mole_fractions[0],
            x2=mole_fractions[1],
        )
    else:
        exp_data = None

    plot_data = {"temperatures": temperatures, "mix_densities": mix_densities}
    data = {
        "GNN": [temperatures, mix_densities],
        "legends": [
            "GNN",
            "GNN",
            "Exp. Mix. Density (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(exp_data),
    }

    plot_id = f"mix_den_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Mix density plot (mol/m³)"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "Temperature (K)",
        "Density plot (mol/m³)",
        "Density at P={pressure} Pa and mole fractions={mole_fractions}",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="mixture_density",
        data=plot_data,
        html=html,
        message="Mixture density plot generated successfully.",
    )


def plot_mix_vle_pt(
    smiles_list: List[str],
    t_min: float,
    t_max: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a plot of Bubble/Dew points (Pa) for a mixture
    with any number of components.

    Args:
      smiles_list (List[str]): List of mixture SMILES [SMILES_1, SMILES_2, SMILES_3, ...].
      t_min (float): minimum temperature (K) to calculate Bubble/Dew points (Pa)
      t_max (float): maximun temperature (K) to calculate Bubble/Dew points (Pa)
      mole_fractions (List[float]): mole fractions list [X1, X2, X3, ...]
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """

    temperatures, bubble, dew = mix_vp(
        MixVpParams(
            smiles_list=smiles_list,
            mole_fractions=mole_fractions,
            kij_matrix=kij_matrix if kij_matrix else [],
            min_temp=t_min,
            max_temp=t_max,
            npoints=npoints,
        )
    )

    exp_data = (
        retrieve_bubble_pressure_data(smiles_list, mole_fractions[0])
        if len(smiles_list) == 2
        else None
    )

    plot_data = {"x": temperatures, "bubble": bubble, "dew": dew}
    data = {
        "GNN": [temperatures, bubble, dew],
        "legends": [
            "GNN Bubble P.",
            "GNN Dew P.",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(exp_data, y_scale=PA_PER_KPA),
    }
    plot_id = f"bubble_dew_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Bubble/Dew points (Pa)"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "Temperature (K)",
        "Pressure (Pa)",
        "VLE at mole fractions={mole_fractions}",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="bubble_dew",
        data=plot_data,
        html=html,
        message="Bubble/dew plot generated successfully.",
    )


def plot_binary_lle_txx(
    smiles_list: List[str],
    temp_min_and_max: List[float],
    pressure: float,
    mole_fractions: List[float],
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a T-x-x LLE diagram for a binary mixture
    from t_min to t_max K at pressure (Pa). Mole fractions are used as starting value,
    so it needs to be within the two phase region.

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      temp_min_and_max (List[float]): Temperature min and max (K) [t_min, t_max]
        to calculate LLE diagram within
      pressure (float): System pressure (Pa)
      mole_fractions (List[float]): Global mole fractions [x1, x2] used as starting value
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    output = mix_lle(
        MixLLEParams(
            smiles_list=smiles_list,
            mole_fractions=mole_fractions,
            kij_matrix=kij_matrix if kij_matrix else [],
            temperature_min=min(temp_min_and_max),
            temperature_max=max(temp_min_and_max),
            pressure=pressure,
            npoints=npoints,
        )
    )

    if output is None:
        return "Failed to calculate LLE T-x-x for these conditions"

    plot_data = {
        "temperature": output["temperature"],
        "x0": output["x0"],
        "y0": output["y0"],
    }
    data = {
        "GNN": [
            output["temperature"],
            output["x0"],
            output["y0"],
        ],
        "legends": ["GNN - Phase 1", "GNN - Phase 2", "ThermoML Archive**"],
        "TML": _experimental_plot_data(
            retrieve_lle_binary_data(smiles_list, pressure / PA_PER_KPA)
        ),
    }
    plot_id = f"b_lle_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary LLE diagram"></div>
    <script>
    getplot_fixed_y(
        {json.dumps(data)},
        "x<sub>1</sub>",
        "Temperature (K)",
        "LLE at P={pressure} Pa",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_lle",
        data=plot_data,
        html=html,
        message="Binary LLE diagram generated successfully.",
    )


def plot_binary_vle_txy(
    smiles_list: List[str],
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a T-x-y VLE diagram for a binary mixture
    at pressure (Pa).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    output = mix_vle(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        pressure=pressure,
        npoints=npoints,
    )

    if output is None:
        return "Failed to calculate VLE T-x-y for these conditions"

    plot_data = {
        "temperature": output["temperature"],
        "x0": output["x0"],
        "y0": output["y0"],
    }
    data = {
        "GNN": [
            output["temperature"],
            output["x0"],
            output["y0"],
        ],
        "legends": ["GNN - Phase 1", "GNN - Phase 2", "ThermoML Archive**"],
        "TML": _experimental_plot_data(
            retrieve_vle_binary_data(smiles_list, pressure / PA_PER_KPA)
        ),
    }
    plot_id = f"b_vle_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary VLE diagram"></div>
    <script>
    getplot_fixed_y(
        {json.dumps(data)},
        "x<sub>1</sub>, y<sub>1</sub>",
        "Temperature (K)",
        "VLE at P={pressure} Pa",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_vle",
        data=plot_data,
        html=html,
        message="Binary VLE diagram generated successfully.",
    )


def plot_binary_vle_xy(
    smiles_list: List[str],
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a x-y VLE diagram for a binary mixture
    at pressure (Pa).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    output = mix_vle(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        pressure=pressure,
        npoints=npoints,
    )

    if output is None:
        return "Failed to calculate VLE x-y for these conditions"

    plot_data = {"x0": output["x0"], "y0": output["y0"]}
    data = {
        "GNN": [
            output["x0"],
            output["y0"],
        ],
        "legends": ["GNN", "GNN", "ThermoML Archive**"],
        "TML": [[], []],
    }
    plot_id = f"b_vle_xy_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary VLE diagram"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "x<sub>1</sub>",
        "y<sub>1</sub>",
        "VLE at P={pressure} Pa",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_vle_xy",
        data=plot_data,
        html=html,
        message="Binary x-y VLE diagram generated successfully.",
    )


def plot_binary_vle_pxy(
    smiles_list: List[str],
    temperature: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a P-x-y VLE diagram for a binary mixture
    at Temperature (K).

    Args:
      smiles_list (List[str]): List with binary SMILES [SMILES_1, SMILES_2].
      temperature (float): System Temperature (K)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 2
    ), f"smiles_list should have 2 SMILES, got {len(smiles_list)} instead"

    xs, bps, dps = mix_vle_pxy(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        temperature=temperature,
        npoints=npoints,
    )

    plot_data = {
        "bubble_points": bps,
        "dew_points": dps,
        "x1s": xs,
    }
    data = {
        "GNN": [
            xs,
            bps,
            dps,
        ],
        "legends": [
            "GNN Bubble P.",
            "GNN Dew P.",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(
            retrieve_vle_pxy_binary_data(smiles_list, temperature), y_scale=PA_PER_KPA
        ),
    }
    plot_id = f"b_vle_pxy_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Binary VLE P-x-y diagram"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "x<sub>1</sub>, y<sub>1</sub>",
        "Pressure (Pa)",
        "VLE at T={temperature} K",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="binary_vle_pxy",
        data=plot_data,
        html=html,
        message="Binary VLE P-x-y diagram generated successfully.",
    )


def plot_ternary_vle_pxy(
    smiles_list: List[str],
    temperature: float,
    solvent_ratio: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 100,
):
    """
    When asked, use this tool to show the user a P-x-y VLE diagram for a ternary mixture
    at fixed Temperature (K) and solvent ratio.

    Solvent_ratio = x2 / (x2 + x3). The first component is scanned in composition.

    Args:
      smiles_list (List[str]): List with ternary SMILES [SMILES_1, SMILES_2, SMILES_3].
      temperature (float): System Temperature (K).
      solvent_ratio (float): Solvent_ratio = x2 / (x2 + x3).
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 100 data points.

    """
    assert (
        len(smiles_list) == 3
    ), f"smiles_list should have 3 SMILES, got {len(smiles_list)} instead"

    xs, bps, dps = mix_ternary_vle_tx_fixed(
        TernaryVleTxParams(
            smiles_list=smiles_list,
            kij_matrix=kij_matrix if kij_matrix else [],
            temperature=temperature,
            solvent_ratio=solvent_ratio,
            npoints=npoints,
        )
    )

    plot_data = {
        "bubble_points": bps,
        "dew_points": dps,
        "x1s": xs,
    }
    data = {
        "GNN": [
            xs,
            bps,
            dps,
        ],
        "legends": [
            "GNN Bubble P.",
            "GNN Dew P.",
            "Exp. Bubble P. (ThermoML Archive**)",
        ],
        "TML": _experimental_plot_data(
            retrieve_vle_ternary_tx_fixed_data(smiles_list, temperature, solvent_ratio),
            y_scale=PA_PER_KPA,
        ),
    }
    plot_id = f"t_vle_pxy_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Ternary VLE P-x-y diagram"></div>
    <script>
    getplot(
        {json.dumps(data)},
        "x<sub>1</sub>, y<sub>1</sub>",
        "Pressure (Pa)",
        "VLE at T={temperature} K and x2/(x2+x3)={solvent_ratio}",
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="ternary_vle_pxy",
        data=plot_data,
        html=html,
        message="Ternary VLE P-x-y diagram generated successfully.",
    )


def plot_ternary_lle_or_vle(
    smiles_list: List[str],
    temperature: float,
    pressure: float,
    kij_matrix: Optional[List[List[float]]] = None,
    npoints: int = 25,
):
    """
    When asked, use this tool to show the user a LLE or VLE diagram for a ternary mixture
    at temperature (K) and pressure (Pa).

    Args:
      smiles_list (List[str]): List with ternary SMILES [SMILES_1, SMILES_2, SMILES_3].
      temperature (float): System temperature (K)
      pressure (float): System pressure (Pa)
      kij_matrix (Optional[List[List[float]]]): A matrix of binary interaction parameters. Optional.
      npoints (int): Number of data points to calculate. Default is 25 data points.

    """
    assert (
        len(smiles_list) == 3
    ), f"smiles_list should have 3 SMILES, got {len(smiles_list)} instead"

    output = mix_ternary_lle(
        smiles_list=smiles_list,
        kij_matrix=kij_matrix if kij_matrix else [],
        temperature=temperature,
        pressure=pressure,
        npoints=npoints,
    )
    experimental_rows = [
        data
        for data in (
            retrieve_lle_ternary_data(smiles_list, pressure / PA_PER_KPA, temperature),
            retrieve_vle_ternary_data(smiles_list, pressure / PA_PER_KPA, temperature),
        )
        if data is not None and data.size > 0
    ]
    if experimental_rows:
        experimental_data = np.vstack(experimental_rows)
        output.update(
            {
                "exp_x0": experimental_data[:, 0].tolist(),
                "exp_x1": experimental_data[:, 1].tolist(),
                "exp_x2": (
                    1.0 - experimental_data[:, 0] - experimental_data[:, 1]
                ).tolist(),
            }
        )
    else:
        output.update({"exp_x0": [], "exp_x1": [], "exp_x2": []})
    plot_data = output
    plot_id = f"t_lle_plot_{uuid.uuid4().hex}"
    html = f"""
    <div id="{plot_id}" alt="Ternary LLE/VLE diagram"></div>
    <script>
    get_ternary_lle_phase_diagram(
        {json.dumps(output)},
        {temperature},
        {pressure},
        "{plot_id}");
    </script>
    """
    return _make_plot_response(
        plot_type="ternary_lle_or_vle",
        data=plot_data,
        html=html,
        message="Ternary LLE/VLE diagram generated successfully.",
    )
