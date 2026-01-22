// plots the GNN ePC-SAFT model results
// and the ThermoML archive data

function get_layout(xlegendpos = 0, xtitle = "", ytitle = "", title = "") {
  return {
    title: { text: title },
    font: {
      family: "Times New Roman",
    },
    legend: {
      x: xlegendpos,
      y: 1,
      font: { family: "monospace", size: 10 },
    },
    paper_bgcolor: "#f8f9fa",
    plot_bgcolor: "#f8f9fa",
    margin: {
      b: 80,
      t: 50,
      l: 80,
      r: 20,
    },
    xaxis: {
      title: {
        text: xtitle,
      },
      linecolor: "black",
      ticks: "inside",
      minor: {
        ticks: "inside",
      },
      mirror: true,
      showline: true,
      showgrid: false,
    },
    yaxis: {
      title: {
        text: ytitle,
      },
      linecolor: "black",
      ticks: "inside",
      minor: {
        ticks: "inside",
      },
      mirror: true,
      showline: true,
      showgrid: false,
    },
    autosize: true,
    showlegend: true,
  };
}

function getplot(data, xlegendpos, ytitle, id, trace_name = "GNN") {
  var trace1 = {
    x: data[1][0],
    y: data[1][1],
    mode: "markers",
    type: "scatter",
    name: "ThermoML Archive**",
    marker: {
      symbol: "x",
      color: "black",
    },
  };

  var trace2 = {
    x: data[0][0],
    y: data[0][1],
    mode: "lines",
    type: "scatter",
    name: trace_name,
  };

  var layout = get_layout(xlegendpos, "Temperature (K)", ytitle);

  var plot_data = [trace1, trace2];

  Plotly.newPlot(id, plot_data, layout, {
    responsive: true,
    modeBarButtonsToRemove: ["select2d", "lasso2d"],
  });
}

function get_phase_diagram(phase_diagram_data, xlegendpos, ytitle, id) {
  var trace1 = {
    y: phase_diagram_data[0],
    x: phase_diagram_data[1],
    mode: "lines",
    type: "scatter",
    name: "Liquid",
  };
  var trace2 = {
    y: phase_diagram_data[0],
    x: phase_diagram_data[2],
    mode: "lines",
    type: "scatter",
    name: "Vapor",
  };

  var layout = get_layout(xlegendpos, "Density (mol / m³)", ytitle);

  var plot_data = [trace1, trace2];

  Plotly.newPlot(id, plot_data, layout, {
    responsive: true,
    modeBarButtonsToRemove: ["select2d", "lasso2d"],
  });
}

function get_ternary_lle_phase_diagram(ternary_lle_phase_diagram_data, id) {
  var trace1 = {
    a: ternary_lle_phase_diagram_data["x0"],
    b: ternary_lle_phase_diagram_data["x1"],
    c: ternary_lle_phase_diagram_data["x2"],
    mode: "markers",
    type: "scatterternary",
    name: "Liquid phase 1",
  };

  var trace2 = {
    a: ternary_lle_phase_diagram_data["y0"],
    b: ternary_lle_phase_diagram_data["y1"],
    c: ternary_lle_phase_diagram_data["y2"],
    mode: "markers",
    type: "scatterternary",
    name: "Liquid phase 2",
  };

  Plotly.newPlot(
    id,
    [trace1, trace2],
    {
      title: "Ternary LLE",
      font: {
        family: "Times New Roman",
      },
      legend: {
        orientation: "h",
        font: { family: "monospace", size: 10 },
      },
      paper_bgcolor: "#f8f9fa",
      plot_bgcolor: "#f8f9fa",
      margin: {
        b: 50,
        t: 50,
        l: 50,
        r: 50,
      },
      autosize: true,
      showlegend: true,
      ternary: {
        sum: 1,
        aaxis: {
          title: { text: "A" },
          min: 0,
          linewidth: 2,
        },
        baxis: {
          title: { text: "B" },
          min: 0,
          linewidth: 2,
        },
        caxis: {
          title: { text: "C" },
          min: 0,
          linewidth: 2,
        },
      },
    },
    {
      responsive: true,
      modeBarButtonsToRemove: ["select2d", "lasso2d"],
    },
  );
}

function get_binary_phase_diagram(temperatures, phase1_x, phase2_x, title, id) {
  var trace1 = {
    x: phase1_x,
    y: temperatures,
    mode: "lines",
    type: "scatter",
    name: "Phase 1",
  };
  var trace2 = {
    x: phase2_x,
    y: temperatures,
    mode: "lines",
    type: "scatter",
    name: "Phase 2",
  };

  Plotly.newPlot(
    id,
    [trace1, trace2],
    get_layout(0, "x<sub>1</sub>", "Temperature (K)", title),
    {
      responsive: true,
      modeBarButtonsToRemove: ["select2d", "lasso2d"],
    },
  );
}

function get_binary_vle_phase_diagram_xy(x0, y0, id) {
  var trace1 = {
    x: x0,
    y: y0,
    mode: "lines",
    type: "scatter",
    name: "VLE",
  };

  Plotly.newPlot(
    id,
    [trace1],
    get_layout(0, "x<sub>1</sub>", "y<sub>1</sub>"),
    {
      responsive: true,
      modeBarButtonsToRemove: ["select2d", "lasso2d"],
    },
  );
}
