import { t } from "../../i18n";
export function getOption(solves, fails) {
  let option = {
    title: {
      left: "center",
      text: t("Solve Percentages"),
    },
    tooltip: {
      trigger: "item",
    },
    toolbox: {
      show: true,
      feature: {
        saveAsImage: { title: t("Save as image") },
      },
    },
    legend: {
      orient: "vertical",
      top: "middle",
      right: 0,
      data: [t("Fails"), t("Solves")],
    },
    series: [
      {
        name: t("Solve Percentages"),
        type: "pie",
        radius: ["30%", "50%"],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: "center",
        },
        itemStyle: {
          normal: {
            label: {
              show: true,
              formatter: function (data) {
                return `${data.name} - ${data.value} (${data.percent}%)`;
              },
            },
            labelLine: {
              show: true,
            },
          },
          emphasis: {
            label: {
              show: true,
              position: "center",
              textStyle: {
                fontSize: "14",
                fontWeight: "normal",
              },
            },
          },
        },
        emphasis: {
          label: {
            show: true,
            fontSize: "30",
            fontWeight: "bold",
          },
        },
        labelLine: {
          show: false,
        },
        data: [
          {
            value: fails,
            name: t("Fails"),
            itemStyle: { color: "#c2410c" },
          },
          {
            value: solves,
            name: t("Solves"),
            itemStyle: { color: "#157a4a" },
          },
        ],
      },
    ],
  };
  return option;
}
