document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase and Chart.js dependencies
    var firebaseConfig = {
        apiKey: "AIzaSyC-pK6Lr4MKPd4mu62MtO-Uoj-HDB6mOMQ",
        authDomain: "csci321-fyp.firebaseapp.com",
        databaseURL: "https://csci321-fyp-default-rtdb.asia-southeast1.firebasedatabase.app",
        projectId: "csci321-fyp",
        storageBucket: "csci321-fyp.appspot.com",
        messagingSenderId: "219030926951",
        appId: "1:219030926951:web:615bf8f380ab41a9adc6c2",
        measurementId: "G-Z12JLB6SWF"
    };

    firebase.initializeApp(firebaseConfig);
    firebase.analytics();

    fetchSubscriptionData();

    // Fetching and displaying data for the top price area
    fetchData().then(data => {
        displayData(data);
    });

    // Declare fetchData using function declaration
    function fetchData() {
        return new Promise(resolve => {
            resolve({
                visits: 200,
                newCustomers: 5,
                valuation: 30,
                visitDuration: '5m 01s',
                priceArea: [
                    { area: 'Orchard', percent: 35 },
                    { area: 'Sentosa', percent: 26 },
                    { area: 'AMK', percent: 18 },
                    { area: 'Bedok', percent: 14 },
                    { area: 'Toa Payoh', percent: 10 },
                    { area: 'Woodlands', percent: 7 }
                ]
            });
        });
    }

    // Fetch and display data
    function displayData(data) {
        if (data) {
            document.getElementById('visits').textContent = `${data.visits}`;
            document.getElementById('newCust').textContent = `${data.newCustomers}`;
            document.getElementById('valuation').textContent = `${data.valuation}`;
            document.getElementById('visitDuration').textContent = `${data.visitDuration}`;

            const priceAreaElement = document.getElementById('priceArea');
            priceAreaElement.innerHTML = ''; // Clear any existing content
            data.priceArea.forEach(item => {
                const row = document.createElement('div');
                row.className = 'row';

                const label = document.createElement('label');
                label.textContent = `${item.area}:`;
                label.style.flex = '1%'; // Flex attribute for label
                label.style.paddingLeft = "2%";

                const barContainer = document.createElement('div');
                barContainer.className = 'bar-container';
                barContainer.style.flex = '4'; // Flex attribute for bar container

                const bar = document.createElement('div');
                bar.style.width = `${item.percent}%`;
                bar.style.backgroundColor = '#007BFF';
                bar.style.color = 'white';
                bar.textContent = `${item.percent}%`; // Text inside the bar
                bar.className = 'bar';

                barContainer.appendChild(bar);
                row.appendChild(label);
                row.appendChild(barContainer);
                priceAreaElement.appendChild(row);
            });
        }
    }

    // Firebase Data fetch for Subscription Pie Chart
    function fetchSubscriptionData() {
        const databaseRef = firebase.database().ref('userData'); // Adjust this path as needed
        databaseRef.once('value', snapshot => {
            if (!snapshot.exists()) {
                console.log("No data available");
                return;
            }
            const subscriptionTypes = { 'Basic': 0, 'Monthly': 0, 'Quarterly': 0, 'Annual': 0 };
            snapshot.forEach(childSnapshot => {
                const user = childSnapshot.val();
                const subscriptionType = user.Subscription;  // Assuming 'Subscription' is the correct key
                if (subscriptionTypes.hasOwnProperty(subscriptionType)) {
                    subscriptionTypes[subscriptionType]++;  // Increment the count for the subscription type
                } else {
                    console.log("Unexpected subscription type: ", subscriptionType);
                }
            });
            console.log("Subscription Types: ", subscriptionTypes);
            if (Object.keys(subscriptionTypes).length > 0) {
                displaySubscriptionChart(subscriptionTypes);
            } else {
                console.log("No subscription types found");
            }
        }).catch(error => {
            console.error("Error fetching data: ", error);
        });
    }

    // Display Subscription Pie Chart
    const displaySubscriptionChart = (subscriptionTypes) => {
        const ctx = document.getElementById('subscriptionPieChart').getContext('2d');
    
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(subscriptionTypes),
                datasets: [{
                    data: Object.values(subscriptionTypes),
                    backgroundColor: [
                        '#4169E1',
                        '#6495ED',
                        '#89CFF0',
                        '#40B5AD'
                    ],
                    borderColor: 'transparent',
                    borderWidth: 0
                    
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw}`;
                            }
                        }
                    }
                }
            }
        });
    };

    displayData();
    fetchSubscriptionData();
});
