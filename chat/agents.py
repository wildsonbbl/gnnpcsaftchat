"google adk agent"

import os
import textwrap
from typing import List, Optional

from gnnepcsaft_mcp_server.utils import (
    batch_critical_points,
    batch_inchi_to_smiles,
    batch_molecular_weights,
    batch_predict_pcsaft_parameters,
    batch_pure_density,
    batch_pure_h_lv,
    batch_pure_vapor_pressure,
    batch_smiles_to_inchi,
    mixture_density,
    mixture_vapor_pressure,
)
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .plot_utils import (
    plot_3d_molecule,
    plot_binary_lle,
    plot_binary_vle,
    plot_binary_vle_xy,
    plot_mix_density,
    plot_mix_vp,
    plot_pure_density,
    plot_pure_h_lv,
    plot_pure_phase_diagram_t_rho,
    plot_pure_surface_tension,
    plot_pure_vapor_pressure,
    plot_ternary_lle,
)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# Default model
DEFAULT_MODEL = "gemini-3-flash-preview"


all_tools = [
    batch_predict_pcsaft_parameters,
    batch_critical_points,
    plot_pure_density,
    plot_pure_vapor_pressure,
    plot_pure_h_lv,
    plot_pure_surface_tension,
    plot_pure_phase_diagram_t_rho,
    plot_mix_density,
    plot_mix_vp,
    plot_binary_lle,
    plot_binary_vle,
    plot_binary_vle_xy,
    plot_ternary_lle,
    plot_3d_molecule,
    batch_inchi_to_smiles,
    batch_smiles_to_inchi,
    batch_molecular_weights,
    batch_pure_density,
    batch_pure_h_lv,
    batch_pure_vapor_pressure,
    mixture_density,
    mixture_vapor_pressure,
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
        instruction=textwrap.dedent(
            """
        You are a helpful assistant for the GNNPCSAFT Chat app. 
        GNNPCSAFT estimates the pure-component parameters of the 
        PC-SAFT equation of state. When the user makes the tools 
        available to you, you can calculate thermodynamic 
        properties using PC-SAFT.
        The user might give you some other tools/functions to use. 
        Make sure to check the tools available in the last 
        user message and their descriptions, then use them when needed.  
        """
        ),
        tools=tools_,
    )
