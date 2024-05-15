// Initialize Firebase
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
  };
  
  firebase.initializeApp(firebaseConfig);
  
  // Get a reference to the Firebase database
  const database = firebase.database();
  
  // Function to handle form submission
  document.getElementById('filterForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission from reloading the page
    
    // Get input values
    const town = document.getElementById('town').value;
    const storeyRange = document.getElementById('storey_range').value;
  
    // Query the database
    const queryRef = database.ref('finaltestupload2')
                          .orderByChild('town')
                          .equalTo(town);
  
    // Listen for changes and update UI in real-time
    queryRef.on('value', function(snapshot) {
      const filteredResults = snapshot.val();
  
      // Filter results by storey range
      const filteredByStoreyRange = Object.entries(filteredResults || {})
                                          .filter(([key, value]) => value.storey_range === storeyRange)
                                          .map(([key, value]) => value);
  
      // Display filtered results in HTML
      displayFilteredResults(filteredByStoreyRange);
    });
  });
  
  // Function to display filtered results in HTML
  function displayFilteredResults(results) {
    const filteredResultsElement = document.getElementById('filteredResults');
    filteredResultsElement.innerHTML = '';
  
    if (results.length > 0) {
      const list = document.createElement('ul');
      results.forEach(result => {
        const listItem = document.createElement('li');
        listItem.textContent = `${result.town}, ${result.storey_range}`;
        list.appendChild(listItem);
      });
      filteredResultsElement.appendChild(list);
    } else {
      filteredResultsElement.textContent = 'No results found.';
    }
  }
  