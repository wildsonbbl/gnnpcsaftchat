// plots the GNN PC-SAFT model results
// and the ThermoML archive data

function get_layout(xtitle = "", ytitle = "", title = "") {
  return {
    title: { text: title },
    font: {
      family: "Times New Roman",
      size: 10,
    },
    legend: {
      x: 0,
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

function getplot(alldata, xtitle, ytitle, title, id) {
  var trace1 = {
    x: alldata["TML"][0],
    y: alldata["TML"][1],
    mode: "markers",
    type: "scatter",
    name: alldata["legends"][2],
    marker: {
      symbol: "x",
      color: "black",
    },
  };

  var trace2 = {
    x: alldata["GNN"][0],
    y: alldata["GNN"][1],
    mode: "lines",
    type: "scatter",
    name: alldata["legends"][0],
  };

  var layout = get_layout(xtitle, ytitle, title);

  var plot_data = [trace1, trace2];

  if (alldata["GNN"][2]) {
    var trace3 = {
      x: alldata["GNN"][0],
      y: alldata["GNN"][2],
      mode: "lines",
      type: "scatter",
      name: alldata["legends"][1],
    };
    var plot_data = [trace1, trace2, trace3];
  }

  Plotly.newPlot(id, plot_data, layout, {
    responsive: true,
    modeBarButtonsToRemove: ["select2d", "lasso2d", "toImage"],
  });
}

function getplot_fixed_y(alldata, xtitle, ytitle, title, id) {
  var trace1 = {
    x: alldata["TML"][1],
    y: alldata["TML"][0],
    mode: "markers",
    type: "scatter",
    name: alldata["legends"][2],
    marker: {
      symbol: "x",
      color: "black",
    },
  };

  var trace2 = {
    x: alldata["GNN"][1],
    y: alldata["GNN"][0],
    mode: "lines",
    type: "scatter",
    name: alldata["legends"][0],
  };

  var layout = get_layout(xtitle, ytitle, title);

  var plot_data = [trace1, trace2];

  if (alldata["GNN"][2]) {
    var trace3 = {
      x: alldata["GNN"][2],
      y: alldata["GNN"][0],
      mode: "lines",
      type: "scatter",
      name: alldata["legends"][1],
    };
    var plot_data = [trace1, trace2, trace3];
  }

  Plotly.newPlot(id, plot_data, layout, {
    responsive: true,
    modeBarButtonsToRemove: ["select2d", "lasso2d", "toImage"],
  });
}

function get_ternary_lle_phase_diagram(
  ternary_lle_phase_diagram_data,
  temperature,
  pressure,
  id,
) {
  var trace1 = {
    a: ternary_lle_phase_diagram_data["x0"],
    b: ternary_lle_phase_diagram_data["x1"],
    c: ternary_lle_phase_diagram_data["x2"],
    mode: "markers",
    type: "scatterternary",
    name: "Phase 1",
  };

  var _ternaryTitle =
    "LLE/VLE at T=" + temperature + " K and P=" + pressure + " Pa";

  var trace2 = {
    a: ternary_lle_phase_diagram_data["y0"],
    b: ternary_lle_phase_diagram_data["y1"],
    c: ternary_lle_phase_diagram_data["y2"],
    mode: "markers",
    type: "scatterternary",
    name: "Phase 2",
  };

  var trace3 = {
    a: ternary_lle_phase_diagram_data["exp_x0"],
    b: ternary_lle_phase_diagram_data["exp_x1"],
    c: ternary_lle_phase_diagram_data["exp_x2"],
    mode: "markers",
    type: "scatterternary",
    name: "ThermoML Archive**",
    marker: {
      symbol: "x",
      color: "black",
    },
  };

  Plotly.newPlot(
    id,
    [trace1, trace2, trace3],
    {
      title: _ternaryTitle,
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
      modeBarButtonsToRemove: ["select2d", "lasso2d", "toImage"],
    },
  );
}
