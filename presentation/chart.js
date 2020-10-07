
google.charts.load('current', {
    callback: function () {
        // Object returned by createDataSet() is duck-typed like
        // the return value of a charts AJAX call.
        drawDashboards(createDataset());
    },
    packages: ['controls', 'corechart', 'line', 'bar']
});

function drawDashboards(response) {

    drawLineChart(response);
    drawPieChart(response);
    drawColumnChart(response);
}

////////////////////////////////////////
//
// LINE CHART
//
////////////////////////////////////////

function drawLineChart(response) {
    var dt = response.getDataTable();
    var startDate = dt.getColumnRange(0).min;
    var endDate = dt.getColumnRange(0).max;
    var chartWidth = '74%'

    var dailyDataChart = new google.visualization.ChartWrapper({
        chartType: 'LineChart',
        containerId: 'lineChart_chart_div',
        dataTable: dt,
        options: {
            title: 'Cumulative Data (Log Scale)',
            legend: 'right',
            width: 1024,
            height: 500,
            chartArea: {
                height: '80%',
                width: chartWidth
            },
            vAxis: {
                scaleType: 'log'
            },
            view: {
                columns: [
                    {
                        calc: function (dataTable, rowIndex) {
                            return dataTable.getFormattedValue(rowIndex, 0);
                        },
                        type: 'string'
                    }, 1, 2, 3]
            }
        }
    });

    var control = new google.visualization.ControlWrapper({
        controlType: 'ChartRangeFilter',
        containerId: 'lineChart_control_div',
        options: {
            // Filter by the date axis.
            filterColumnIndex: 0,
            ui: {
                chartType: 'LineChart',
                chartOptions: {
                    chartArea: {
                        width: '500px'
                    },
                    hAxis: {
                        baselineColor: 'none'
                    }
                },
                // Display a single series that shows the number of cases
                // Thus, this view has two columns: the date (axis) and the stock value (line series).
                chartView: {
                    columns: [0, 1]
                },
                // 1 day in milliseconds = 24 * 60 * 60 * 1000 = 86,400,000
                minRangeSize: 86400000
            }
        },
        // Initial range
        state: {
            range: {
                start: startDate,
                end: endDate
            }
        }
    });

    new google.visualization.Dashboard(document.getElementById('lineChart_dashboard_div')).
        bind(control, dailyDataChart).
        draw(dt);
}

////////////////////////////////////////
//
// PIE CHART
//
////////////////////////////////////////

function drawPieChart(response) {

    var dt = response.getDataTable();
    var rowCount = dt.getNumberOfRows();
    var pieView = new google.visualization.DataView(dt)
    var startDate = dt.getColumnRange(0).min;
    var endDate = dt.getColumnRange(0).max;
    var pieDate = endDate;

    // Define a DateRangeFilter slider control for the 'Year' column.
    var slider = new google.visualization.ControlWrapper({
        controlType: 'DateRangeFilter',
        containerId: 'pieChart_control_div',
        options: {
            filterColumnLabel: 'Date',
            lowThumbAtMinimum: true,
            ui: {
                format: {
                    pattern: 'yyyy-MM-dd'
                }
            }
        },
        dataTable: dt,
        state: {
            range: {
                start: startDate,
                end: endDate
            }
        },
        view: {
            columns: [0]
        }
    });

    var v = setUpPieView()

    var pieChart = new google.visualization.ChartWrapper({
        chartType: 'PieChart',
        containerId: 'pieChart_chart_div',
        dataTable: v,
        options: {
            title: pieTitle(pieDate),
            legend: 'right',
            width: 450,
            height: 300,
            is3D: true,
            titleTextStyle: {
                fontSize: 14,
                bold: true
            },
            legend: {
                textStyle: {
                    fontSize: 14
                }
            }
        }
    });

    google.visualization.events.addListener(slider, 'statechange', updatePieView);
    slider.draw();
    pieChart.draw();

    // Hide min range slider details as we don't want it for this chart
    document.getElementsByClassName("google-visualization-controls-slider-thumb")[0].style.opacity = 0;
    document.getElementsByClassName('google-visualization-controls-rangefilter-thumblabel')[0].style.display = 'none'

    function setUpPieView() {

        pieDate = (function () {
            var state = slider.getState();

            if ('range' in state) {
                return state.range.end;
            }

            return state.highValue;

        })();

        pieView.setRows(0, rowCount - 1);

        //latestDate = pieView.getColumnRange(0).date;
        latestRow = pieView.getFilteredRows([{ column: 0, minValue: pieDate, maxValue: new Date(pieDate.getTime() + 86400000) }]).shift();

        if (isNaN(latestRow) || latestRow < 1) {
            latestRow = 1
        }

        pieView.hideRows(0, latestRow - 1);

        if (latestRow < rowCount - 1) {
            pieView.hideRows(latestRow + 1, rowCount - 1)
        }

        return transposeDateDataTable(pieView)
    }

    function updatePieView() {

        var v = setUpPieView();
        pieChart.setDataTable(v);
        pieDate = v.getValue(0, 2);
        pieChart.setOption('title', pieTitle(pieDate));
        pieChart.draw();
    }

    function pieTitle(date) {

        return 'Distribution by Day\n' + date.toLocaleDateString("en-US", { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }

    function transposeDateDataTable(dataTable) {

        // Create new datatable
        var newDataTable = new google.visualization.DataTable();

        // Add first column from original datatable
        newDataTable.addColumn('string', 'Metric');

        // Convert column labels to row labels
        for (var x = 1; x < dataTable.getNumberOfColumns(); x++) {
            var label = dataTable.getColumnLabel(x);
            newDataTable.addRow([label]);
        }

        // Convert row labels and data to columns
        // Last column is date. Not displayed but used for slider filter
        for (var x = 0; x < dataTable.getNumberOfRows(); x++) {
            newDataTable.addColumn('number', 'Number');
            newDataTable.addColumn('date', 'Date')
            for (var y = 1; y < dataTable.getNumberOfColumns(); y++) {
                newDataTable.setValue(y - 1, x + 1, dataTable.getValue(x, y));
                newDataTable.setValue(y - 1, x + 2, dataTable.getValue(x, 0));
            }
        }

        return newDataTable;
    }
}

////////////////////////////////////////
//
// COLUMN CHART
//
////////////////////////////////////////


function drawColumnChart(response) {

    // Create view of dataset grouped by month and the max value of each column for the month
    // The values on each day are cumulative
    var tableView = google.visualization.data.group(
        response.getDataTable(),
        [
            {
                column: 0, modifier: function (date) {
                    var m = date.getMonth() + 1;
                    return date.getFullYear() + '-' + (m < 10 ? '0' + m : m);
                },
                type: 'string',
                label: 'Month'
            }
        ],
        [
            { 'column': 1, 'aggregation': google.visualization.data.max, 'type': 'number' },
            { 'column': 2, 'aggregation': google.visualization.data.max, 'type': 'number' },
            { 'column': 3, 'aggregation': google.visualization.data.max, 'type': 'number' }
        ]);

    // Walk backwards through the view subtracting the previous month's total from this month's
    // to get monthly totals
    for (var row = tableView.getNumberOfRows() - 1; row > 0; --row) {
        var newRow = [tableView.getValue(row, 0)];
        for (var col = 1; col <= 3; ++col) {
            var v1 = tableView.getValue(row, col);
            var v2 = tableView.getValue(row - 1, col);
            tableView.setValue(row, col, v1 - v2)
        }
    }

    var columnChart = new google.visualization.ChartWrapper({
        chartType: 'Bar',
        containerId: 'table_chart_div',
        dataTable: tableView,
        options: {
            width: 550,
            height: 400,
            title: 'display me please',
            titleTextStyle: {
                fontSize: 8,
                bold: true
            },
            hAxis: {
                slantedText: true
            },
            vAxis: {
                scaleType: 'log'
            },
            legend: {
                position: 'right',
                textStyle: {
                    fontName: 'arial',
                    fontSize: 6
                }
            }
        }

    });

    columnChart.draw();
}
