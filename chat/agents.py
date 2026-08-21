"google adk agent"

import os
import textwrap
from typing import List, Optional

from gnnepcsaft_mcp_server.utils import (
    batch_critical_points,
    batch_inchi_to_smiles,
    batch_predict_pcsaft_parameters,
    batch_smiles_to_inchi,
)
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .plot_utils import (
    plot_3d_molecule,
    plot_binary_lle_txx,
    plot_binary_vle_pxy,
    plot_binary_vle_txy,
    plot_binary_vle_xy,
    plot_mix_density,
    plot_mix_vle_pt,
    plot_pure_density,
    plot_pure_h_lv,
    plot_pure_phase_diagram_t_rho_and_p_rho,
    plot_pure_surface_tension,
    plot_pure_vapor_pressure,
    plot_ternary_lle_or_vle,
)
from .utils_data import (
    retrieve_available_data_binary,
    retrieve_available_data_pure,
    retrieve_available_data_ternary,
)
from .utils_kij import optimize_binary_kij_with_vle

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# Default model
DEFAULT_MODEL = "gemini-3.7-flash"


all_tools = [
    batch_predict_pcsaft_parameters,
    batch_critical_points,
    plot_pure_density,
    plot_pure_vapor_pressure,
    plot_pure_h_lv,
    plot_pure_surface_tension,
    plot_pure_phase_diagram_t_rho_and_p_rho,
    plot_mix_density,
    plot_mix_vle_pt,
    plot_binary_lle_txx,
    plot_binary_vle_txy,
    plot_binary_vle_xy,
    plot_binary_vle_pxy,
    plot_ternary_lle_or_vle,
    optimize_binary_kij_with_vle,
    retrieve_available_data_pure,
    retrieve_available_data_binary,
    retrieve_available_data_ternary,
    plot_3d_molecule,
    batch_inchi_to_smiles,
    batch_smiles_to_inchi,
]


async def create_root_agent(
    model_name: str = DEFAULT_MODEL, tools: Optional[List] = None
):
    """Create a root agent with the specified model"""

    if tools is None:
        tools_ = all_tools
    else:
        tools_ = tools

    return LlmAgent(
        model=(
            model_name if model_name.startswith("gemini") else LiteLlm(model=model_name)
        ),
        name="gnnpcsaft_agent",
        description="Helpfull assistant for the GNNPCSAFT Chat app",
        instruction=textwrap.dedent("""
        You are a helpful assistant for the GNNPCSAFT Chat app. 
        GNNPCSAFT estimates the pure-component parameters of the 
        PC-SAFT equation of state. When the user makes the tools 
        available to you, you can calculate thermodynamic 
        properties using PC-SAFT.
        The user might give you some other tools/functions to use. 
        Make sure to check the tools available in the last 
        user message and their descriptions, then use them when needed.  
        """),
        tools=tools_,
    )
