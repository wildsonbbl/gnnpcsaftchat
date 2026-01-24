# GNNPCSAFT Chat

The GNNPCSAFT Chat is an implementation of [our project](https://github.com/wildsonbbl/gnnepcsaft/) that focuses on using Graph Neural Networks ([GNN](https://en.wikipedia.org/wiki/Graph_neural_network)) to estimate the pure-component parameters of the Equation of State [PC-SAFT](https://en.wikipedia.org/wiki/PC-SAFT). We developed this app so the scientific community can access the model's results easily.

In this app, you can chat with LLM models (Gemini or Ollama) with GNNPCSAFT tools, allowing you to ask questions about the PC-SAFT parameters of various compounds, predict thermodynamic properties, and get insights into the GNNPCSAFT's performance.

On [releases](https://github.com/wildsonbbl/gnnpcsaftchat/releases), you find a electron app for the chat. A container image is also available on [Docker Hub](https://hub.docker.com/r/wildsonbbl/gnnpcsaftchat), and can be run using:

```bash
docker run -p 19771:8000 -e GNNPCSAFTCHAT_OLLAMA_API_BASE=http://host.docker.internal:11434 --add-host=host.docker.internal:host-gateway wildsonbbl/gnnpcsaftchat:latest
```

Access the app at `http://localhost:19771` in your web browser.

Other implementations with GNNPCSAFT:

- [GNNPCSAFT CLI](https://github.com/wildsonbbl/gnnepcsaftcli)
- [GNNPCSAFT APP](https://github.com/wildsonbbl/gnnpcsaftapp)
- [GNNPCSAFT MCP](https://github.com/wildsonbbl/gnnepcsaft_mcp_server)
- [GNNPCSAFT Webapp](https://github.com/wildsonbbl/gnnepcsaftwebapp)
