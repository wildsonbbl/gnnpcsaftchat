"google adk agent"

import os
import textwrap
from typing import List, Optional

from gnnepcsaft_mcp_server.plot_utils import v3000_mol_block
from gnnepcsaft_mcp_server.utils import (
    batch_convert_pure_density_to_kg_per_m3,
    batch_critical_points,
    batch_inchi_to_smiles,
    batch_molecular_weights,
    batch_pa_to_bar,
    batch_predict_epcsaft_parameters,
    batch_pure_density,
    batch_pure_h_lv,
    batch_pure_vapor_pressure,
    batch_smiles_to_inchi,
    mixture_density,
    mixture_phase,
    mixture_vapor_pressure,
    pubchem_description,
    pure_phase,
)
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .plot_utils import plot_pure_density, plot_pure_h_lv, plot_pure_vapor_pressure

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# Default model
DEFAULT_MODEL = "gemini-3-flash-preview"


all_tools = [
    batch_convert_pure_density_to_kg_per_m3,
    batch_critical_points,
    batch_inchi_to_smiles,
    batch_molecular_weights,
    batch_pa_to_bar,
    batch_predict_epcsaft_parameters,
    batch_pure_density,
    batch_pure_h_lv,
    batch_pure_vapor_pressure,
    batch_smiles_to_inchi,
    mixture_density,
    mixture_phase,
    mixture_vapor_pressure,
    pubchem_description,
    pure_phase,
    v3000_mol_block,
    plot_pure_density,
    plot_pure_vapor_pressure,
    plot_pure_h_lv,
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
