const form = document.querySelector("#queryForm");
const dateInput = document.querySelector("#dateInput");
const stockSelect = document.querySelector("#stockSelect");
const customSymbolInput = document.querySelector("#customSymbol");
const addSymbolButton = document.querySelector("#addSymbolButton");
const statusEl = document.querySelector("#status");
const chartTitle = document.querySelector("#chartTitle");
const chartSubtitle = document.querySelector("#chartSubtitle");
const chart = echarts.init(document.querySelector("#chart"));

const palette = [
  "#176b87",
  "#c73e1d",
  "#228b22",
  "#7b3f98",
  "#d18b00",
  "#0b6e4f",
  "#cc4778",
  "#2f5597",
];

function normalizeSymbol(raw) {
  const cleaned = raw.trim().toUpperCase().replace(/\.(SH|SZ|BJ)$/u, "").replace(/^(SH|SZ|BJ)/u, "");
  if (!/^\d{6}$/u.test(cleaned)) {
    throw new Error("请输入 6 位股票代码");
  }
  return cleaned;
}

function lastWeekday() {
  const value = new Date();
  const day = value.getDay();
  if (day === 0) value.setDate(value.getDate() - 2);
  if (day === 6) value.setDate(value.getDate() - 1);
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const date = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${date}`;
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function selectedSymbols() {
  return Array.from(stockSelect.selectedOptions).map((option) => option.value);
}

function addStockOption(symbol, name = "") {
  const existing = Array.from(stockSelect.options).find((option) => option.value === symbol);
  if (existing) {
    existing.selected = true;
    return;
  }
  const option = document.createElement("option");
  option.value = symbol;
  option.textContent = name ? `${symbol} ${name}` : symbol;
  option.selected = true;
  stockSelect.append(option);
}

function getMode() {
  return new FormData(form).get("mode");
}

function renderEmpty(message) {
  chart.clear();
  chart.setOption({
    title: {
      text: message,
      left: "center",
      top: "center",
      textStyle: { color: "#657487", fontSize: 16, fontWeight: 500 },
    },
  });
}

function renderChart(payload) {
  const mode = getMode();
  const yIsPercent = mode === "pct";
  const series = payload.series.map((item) => ({
    name: `${item.symbol} ${item.name}`,
    type: "line",
    showSymbol: false,
    smooth: false,
    sampling: "lttb",
    emphasis: { focus: "series" },
    data: item.points.map((point) => [
      point.time,
      yIsPercent ? point.changePct : point.close,
      point.close,
      point.volume,
      point.amount,
    ]),
  }));

  chart.clear();
  chart.setOption({
    color: palette,
    animation: false,
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
      valueFormatter(value) {
        if (typeof value !== "number") return value;
        return yIsPercent ? `${value.toFixed(2)}%` : value.toFixed(2);
      },
    },
    legend: {
      type: "scroll",
      top: 4,
      left: 8,
      right: 8,
    },
    grid: {
      top: 54,
      left: 58,
      right: 30,
      bottom: 72,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      axisLabel: { color: "#657487" },
      axisLine: { lineStyle: { color: "#d9e0e8" } },
      splitLine: { show: true, lineStyle: { color: "#edf1f5" } },
    },
    yAxis: {
      type: "value",
      scale: !yIsPercent,
      axisLabel: {
        color: "#657487",
        formatter: yIsPercent ? "{value}%" : "{value}",
      },
      splitLine: { lineStyle: { color: "#edf1f5" } },
    },
    dataZoom: [
      { type: "inside", xAxisIndex: 0 },
      { type: "slider", xAxisIndex: 0, height: 26, bottom: 20 },
    ],
    toolbox: {
      right: 10,
      feature: {
        restore: { title: "还原" },
        saveAsImage: { title: "保存图片" },
      },
    },
    series,
  });

  chartTitle.textContent = `${payload.date} 分时曲线`;
  chartSubtitle.textContent = yIsPercent
    ? "纵轴为相对前一交易收盘价的涨跌幅。"
    : "纵轴为 1 分钟收盘价。";
  const warning = payload.errors?.length ? `；${payload.errors.join("；")}` : "";
  setStatus(`${payload.source}${warning}`);
}

async function loadStocks() {
  const response = await fetch("/api/stocks");
  const payload = await response.json();
  stockSelect.innerHTML = "";
  payload.stocks.forEach((stock, index) => {
    const option = document.createElement("option");
    option.value = stock.symbol;
    option.textContent = `${stock.symbol} ${stock.name}`;
    option.selected = index === 0 || index === 5 || index === 7;
    stockSelect.append(option);
  });
}

async function queryMinutes() {
  const date = dateInput.value;
  const symbols = selectedSymbols();
  if (!date) {
    setStatus("请选择日期", true);
    return;
  }
  if (!symbols.length) {
    setStatus("请至少选择一只股票", true);
    return;
  }

  const params = new URLSearchParams({ date, symbols: symbols.join(",") });
  setStatus("正在查询 1 分钟数据...");
  renderEmpty("加载中");

  try {
    const response = await fetch(`/api/minutes?${params.toString()}`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "查询失败");
    }
    renderChart(payload);
  } catch (error) {
    chartTitle.textContent = `${date} 分时曲线`;
    chartSubtitle.textContent = "当前条件未返回可绘制的数据。";
    renderEmpty(error.message);
    setStatus(error.message, true);
  }
}

addSymbolButton.addEventListener("click", () => {
  try {
    const symbol = normalizeSymbol(customSymbolInput.value);
    addStockOption(symbol);
    customSymbolInput.value = "";
    setStatus(`已添加 ${symbol}`);
  } catch (error) {
    setStatus(error.message, true);
  }
});

customSymbolInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    addSymbolButton.click();
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  queryMinutes();
});

window.addEventListener("resize", () => chart.resize());

dateInput.value = lastWeekday();
loadStocks()
  .then(() => queryMinutes())
  .catch((error) => {
    renderEmpty("股票列表加载失败");
    setStatus(error.message, true);
  });
