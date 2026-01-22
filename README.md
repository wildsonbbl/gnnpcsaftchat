# GNNPCSAFT Chat

The GNNPCSAFT Chat is an implementation of [our project](https://github.com/wildsonbbl/gnnepcsaft/) that focuses on using Graph Neural Networks ([GNN](https://en.wikipedia.org/wiki/Graph_neural_network)) to estimate the pure-component parameters of the Equation of State [PC-SAFT](https://en.wikipedia.org/wiki/PC-SAFT). We developed this app so the scientific community can access the model's results easily.

In this app, you can chat with LLM models (Gemini or Ollama) with GNNPCSAFT tools, allowing you to ask questions about the PC-SAFT parameters of various compounds, predict thermodynamic properties, and get insights into the GNNPCSAFT's performance.

You can usually find an app for the project at [SourceForge](https://sourceforge.net/projects/gnnpcsaft/). For this app, it will be available on releases too.

A CLI to use a model can be found at [GNNePCSAFT CLI](https://github.com/wildsonbbl/gnnepcsaftcli) and installed with [pipx](https://github.com/pypa/pipx):

```bash
pipx install gnnepcsaftcli
```
