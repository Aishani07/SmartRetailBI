
const API_URL = "http://127.0.0.1:5000";

// FORMAT CURRENCY
function formatRevenue(value) {
    return "£" + Number(value).toLocaleString("en-GB", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


// LOAD DASHBOARD DATA
async function loadDashboard() {

    try {

        // TOTAL REVENUE
        const salesResponse = await fetch(`${API_URL}/api/sales`);
        const salesData = await salesResponse.json();

        document.getElementById("totalRevenue").textContent =
            formatRevenue(salesData.total_revenue);


        // MONTHLY REVENUE TREND
        const monthlyResponse = await fetch(`${API_URL}/api/monthly-sales`);
        const monthlyData = await monthlyResponse.json();

        const monthFilter = document.getElementById("monthFilter");
        const monthlyInfo = document.getElementById("monthlyRevenueInfo");

        monthlyData.forEach(item => {
            const option = document.createElement("option");
            option.value = item.Month;
            option.textContent = item.Month;
            monthFilter.appendChild(option);
        });

        const salesChart = new Chart(
            document.getElementById("salesChart"),
            {
                type: "line",
                data: {
                    labels: monthlyData.map(item => item.Month),
                    datasets: [{
                        label: "Monthly Revenue",
                        data: monthlyData.map(item => item.Revenue),
                        borderColor: "#1565c0",
                        backgroundColor: "rgba(21, 101, 192, 0.15)",
                        fill: true,
                        tension: 0.3,
                        pointRadius: 5,
                        pointHoverRadius: 9
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: "nearest",
                        intersect: true
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return "Revenue: " +
                                        formatRevenue(context.parsed.y);
                                }
                            }
                        }
                    },
                    onClick: function(event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const month = salesChart.data.labels[index];
                            const revenue = salesChart.data.datasets[0].data[index];

                            monthlyInfo.textContent =
                                month + " Revenue: " + formatRevenue(revenue);
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }
        );

        monthFilter.addEventListener("change", function() {

            const selectedMonth = this.value;

            if (selectedMonth === "all") {

                salesChart.data.labels =
                    monthlyData.map(item => item.Month);

                salesChart.data.datasets[0].data =
                    monthlyData.map(item => item.Revenue);

                monthlyInfo.textContent = "Showing all months.";

            } else {

                const selectedData = monthlyData.find(
                    item => item.Month === selectedMonth
                );

                salesChart.data.labels = [selectedData.Month];
                salesChart.data.datasets[0].data = [selectedData.Revenue];

                monthlyInfo.textContent =
                    selectedData.Month + " Revenue: " +
                    formatRevenue(selectedData.Revenue);
            }

            salesChart.update();
        });


        // COUNTRY-WISE REVENUE
        const countryResponse = await fetch(`${API_URL}/api/countries`);
        const countryData = await countryResponse.json();

        const countryFilter = document.getElementById("countryFilter");
        const countryInfo = document.getElementById("countryRevenueInfo");

        countryData.forEach(item => {
            const option = document.createElement("option");
            option.value = item.Country;
            option.textContent = item.Country;
            countryFilter.appendChild(option);
        });

        const countryChart = new Chart(
            document.getElementById("countryChart"),
            {
                type: "bar",
                data: {
                    labels: countryData.map(item => item.Country),
                    datasets: [{
                        label: "Revenue",
                        data: countryData.map(item => item.Revenue),
                        backgroundColor: "#1565c0"
                    }]
                },
                options: {
                    responsive: true,
                    indexAxis: "y",
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return "Revenue: " +
                                        formatRevenue(context.parsed.x);
                                }
                            }
                        }
                    },
                    onClick: function(event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const country = countryChart.data.labels[index];
                            const revenue = countryChart.data.datasets[0].data[index];

                            countryInfo.textContent =
                                country + ": " + formatRevenue(revenue);

                            countryFilter.value = country;
                        }
                    }
                }
            }
        );

        countryFilter.addEventListener("change", function() {

            const selectedCountry = this.value;

            if (selectedCountry === "all") {

                countryChart.data.labels =
                    countryData.map(item => item.Country);

                countryChart.data.datasets[0].data =
                    countryData.map(item => item.Revenue);

                countryInfo.textContent = "Showing all top 10 countries.";

            } else {

                const selectedData = countryData.find(
                    item => item.Country === selectedCountry
                );

                countryChart.data.labels = [selectedData.Country];
                countryChart.data.datasets[0].data = [selectedData.Revenue];

                countryInfo.textContent =
                    selectedData.Country + ": " +
                    formatRevenue(selectedData.Revenue);
            }

            countryChart.update();
        });


        // CUSTOMER SEGMENTATION
        const segmentResponse = await fetch(`${API_URL}/api/segments`);
        const segmentData = await segmentResponse.json();

        const totalCustomers = segmentData.reduce(
            (total, item) => total + Number(item.CustomerCount),
            0
        );

        document.getElementById("totalCustomers").textContent =
            totalCustomers.toLocaleString("en-GB");

        const segmentInfo = document.getElementById("segmentInfo");

        const segmentChart = new Chart(
            document.getElementById("segmentChart"),
            {
                type: "doughnut",
                data: {
                    labels: segmentData.map(item => item.CustomerSegment),
                    datasets: [{
                        data: segmentData.map(item => item.CustomerCount),
                        backgroundColor: [
                            "#1565c0",
                            "#00897b",
                            "#ef8c32",
                            "#7e57c2",
                            "#e53935",
                            "#78909c"
                        ],
                        hoverOffset: 12
                    }]
                },
                options: {
                    responsive: true,
                    onClick: function(event, elements) {

                        if (elements.length > 0) {

                            const index = elements[0].index;
                            const selected = segmentData[index];

                            segmentInfo.innerHTML = "";

                            const title = document.createElement("strong");
                            title.textContent = selected.CustomerSegment;

                            const count = document.createElement("p");
                            count.textContent =
                                "Customers: " +
                                Number(selected.CustomerCount).toLocaleString("en-GB");

                            const revenue = document.createElement("p");
                            revenue.textContent =
                                "Total Revenue: " +
                                formatRevenue(selected.TotalRevenue);

                            segmentInfo.appendChild(title);
                            segmentInfo.appendChild(count);
                            segmentInfo.appendChild(revenue);
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label + ": " +
                                        context.parsed + " customers";
                                }
                            }
                        },
                        legend: {
                            position: "bottom"
                        }
                    }
                }
            }
        );


        // SALES FORECAST
        const forecastResponse = await fetch(`${API_URL}/api/forecast`);
        const forecastData = await forecastResponse.json();

        const forecastFilter = document.getElementById("forecastFilter");
        const forecastInfo = document.getElementById("forecastInfo");

        forecastData.forEach(item => {
            const option = document.createElement("option");
            option.value = item.Date;
            option.textContent = item.Date;
            forecastFilter.appendChild(option);
        });

        const forecastChart = new Chart(
            document.getElementById("forecastChart"),
            {
                type: "line",
                data: {
                    labels: forecastData.map(item => item.Date),
                    datasets: [{
                        label: "Predicted Revenue",
                        data: forecastData.map(item => item.PredictedRevenue),
                        borderColor: "#ef8c32",
                        backgroundColor: "rgba(239, 140, 50, 0.15)",
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return "Predicted Revenue: " +
                                        formatRevenue(context.parsed.y);
                                }
                            }
                        }
                    },
                    onClick: function(event, elements) {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const item = forecastData[index];

                            forecastFilter.value = item.Date;

                            forecastInfo.textContent =
                                item.Date + " | Predicted Revenue: " +
                                formatRevenue(item.PredictedRevenue);
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }
        );

        forecastFilter.addEventListener("change", function() {

            const selectedDate = this.value;

            if (selectedDate === "all") {

                forecastChart.data.labels =
                    forecastData.map(item => item.Date);

                forecastChart.data.datasets[0].data =
                    forecastData.map(item => item.PredictedRevenue);

                forecastInfo.textContent = "Showing all 30 forecast days.";

            } else {

                const selectedData = forecastData.find(
                    item => item.Date === selectedDate
                );

                forecastChart.data.labels = [selectedData.Date];

                forecastChart.data.datasets[0].data = [
                    selectedData.PredictedRevenue
                ];

                forecastInfo.textContent =
                    selectedData.Date + " | Predicted Revenue: " +
                    formatRevenue(selectedData.PredictedRevenue);
            }

            forecastChart.update();
        });


        // SALES ANOMALIES
        const anomalyResponse = await fetch(`${API_URL}/api/anomalies`);
        const anomalyData = await anomalyResponse.json();

        document.getElementById("totalAnomalies").textContent =
            anomalyData.length;

        const anomalyFilter = document.getElementById("anomalyFilter");
        const anomalyInfo = document.getElementById("anomalyInfo");
        const anomalyList = document.getElementById("anomalyList");

        let anomalyChart;

        function displayAnomalies(filter) {

            let filteredData = anomalyData;

            if (filter === "high") {
                filteredData = anomalyData.filter(
                    item => item.AnomalyType === "Unusually High Sales"
                );
            }

            if (filter === "low") {
                filteredData = anomalyData.filter(
                    item => item.AnomalyType === "Unusually Low Sales"
                );
            }

            if (anomalyChart) {
                anomalyChart.destroy();
            }

            anomalyChart = new Chart(
                document.getElementById("anomalyChart"),
                {
                    type: "bar",
                    data: {
                        labels: filteredData.map(item => item.Date),
                        datasets: [{
                            label: "Unusual Daily Revenue",
                            data: filteredData.map(item => item.Revenue),
                            backgroundColor: "#e53935"
                        }]
                    },
                    options: {
                        responsive: true,
                        onClick: function(event, elements) {

                            if (elements.length > 0) {
                                const index = elements[0].index;
                                const item = filteredData[index];

                                anomalyInfo.textContent =
                                    item.Date + " | " +
                                    item.AnomalyType + " | Revenue: " +
                                    formatRevenue(item.Revenue);
                            }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return "Revenue: " +
                                            formatRevenue(context.parsed.y);
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                }
            );

            anomalyList.innerHTML = "";

            if (filteredData.length === 0) {
                anomalyList.textContent = "No anomalies found.";
                return;
            }

            filteredData.forEach(item => {

                const paragraph = document.createElement("p");

                paragraph.textContent =
                    `${item.Date} | ${item.AnomalyType} | ${formatRevenue(item.Revenue)}`;

                anomalyList.appendChild(paragraph);
            });
        }

        displayAnomalies("all");

        anomalyFilter.addEventListener("change", function() {
            displayAnomalies(this.value);
        });


    } catch (error) {

        console.error("Dashboard loading error:", error);

        alert("Unable to load dashboard. Make sure Flask is running and check the browser console.");
    }
}


// PRODUCT RECOMMENDATION SEARCH
async function searchRecommendations() {

    const product = document.getElementById("productInput").value.trim();
    const resultsDiv = document.getElementById("recommendationResults");

    if (!product) {
        resultsDiv.textContent = "Please enter a product name.";
        return;
    }

    resultsDiv.textContent = "Searching recommendations...";

    try {

        const response = await fetch(
            `${API_URL}/api/recommendations?product=${encodeURIComponent(product)}`
        );

        const data = await response.json();

        if (!response.ok) {
            resultsDiv.textContent =
                data.message || data.error || "Could not find recommendations.";
            return;
        }

        if (data.length === 0) {
            resultsDiv.textContent =
                "No recommendations found. Try another product name.";
            return;
        }

        resultsDiv.innerHTML = "<h4>Recommended Products</h4>";

        data.forEach(item => {

            const paragraph = document.createElement("p");

            paragraph.textContent =
                `${item.RecommendedProduct} | Purchased together: ${item.CoPurchaseCount} times | Confidence: ${(Number(item.Confidence) * 100).toFixed(1)}%`;

            resultsDiv.appendChild(paragraph);
        });

    } catch (error) {

        console.error("Recommendation error:", error);

        resultsDiv.textContent =
            "Unable to connect to the recommendation API.";
    }
}


// RECOMMENDATION BUTTON
document.getElementById("recommendButton").addEventListener(
    "click",
    searchRecommendations
);


// SMARTRETAIL CHATBOT
async function sendMessage() {

    const input = document.getElementById("chatInput");
    const chatWindow = document.getElementById("chatWindow");

    const question = input.value.trim();

    if (!question) {
        return;
    }

    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = question;

    chatWindow.appendChild(userMessage);

    input.value = "";

    try {

        const response = await fetch(`${API_URL}/api/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        const botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.textContent =
            data.answer || data.message || "No answer received.";

        chatWindow.appendChild(botMessage);

    } catch (error) {

        const errorMessage = document.createElement("div");
        errorMessage.className = "bot-message";
        errorMessage.textContent = "Unable to connect to the chatbot.";

        chatWindow.appendChild(errorMessage);

        console.error("Chatbot error:", error);
    }

    chatWindow.scrollTop = chatWindow.scrollHeight;
}


// CHATBOT SEND BUTTON
document.getElementById("sendButton").addEventListener(
    "click",
    sendMessage
);


// SEND CHAT MESSAGE USING ENTER
document.getElementById("chatInput").addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    }
);


// START DASHBOARD
loadDashboard();
