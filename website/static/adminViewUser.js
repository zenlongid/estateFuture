// Import relevant imports
console.log("adminViewUser.js is connected");

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-app.js";
import { getDatabase, ref, set, get, child } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-database.js";

const app = initializeApp(firebaseConfig);

// Function to fetch users from Firebase and reflect in the HTML
async function fetchUsers() {
  const database = getDatabase();
  const usersRef = ref(database, 'users');
  
  const snapshot = await get(usersRef);
  if (snapshot.exists()) {
      const users = snapshot.val();
      const userListBody = document.getElementById('user-list-body');
      userListBody.innerHTML = ''; // Clear the table body

      // Create a table row for each user
      Object.keys(users).forEach((key, index) => {
          const user = users[key];
          const row = document.createElement('tr');

          // // Insert a checkbox
          // const checkCell = document.createElement('td');
          // const checkbox = document.createElement('input');
          // checkbox.type = 'checkbox';
          // checkCell.appendChild(checkbox);
          // row.appendChild(checkCell);

          // Insert the ID
          const idCell = document.createElement('td');
          idCell.textContent = index + 1; // Generate a sequential ID
          row.appendChild(idCell);

          // Insert the name
          const nameCell = document.createElement('td');
          nameCell.textContent = user.name; // Use the 'name' from your Firebase data
          row.appendChild(nameCell);

          // Insert the email
          const emailCell = document.createElement('td');
          emailCell.textContent = user.email; // Use the 'email' from your Firebase data
          row.appendChild(emailCell);

          // Insert the View button
          const actionCell = document.createElement('td');
          const viewButton = document.createElement('button');
          viewButton.textContent = 'View';
          viewButton.className = 'action-button';
          // Add an event listener here if you want to handle the view action
          viewButton.onclick = function() {
            window.location.href = `Admin_UserAccountDetailPage.html?userName=${key}`;
          };
          actionCell.appendChild(viewButton);
          row.appendChild(actionCell);

          // Append the row to the table body
          userListBody.appendChild(row);
      });
  } else {
      console.log("No data available");
  }
}

// Function to search users by name and email
function searchUsers() {
  const searchTerm = document.querySelector('.search-input').value.toLowerCase();

  // Get all the user rows in the table body
  const users = document.querySelectorAll('#user-list-body tr');

  users.forEach(row => {
      // Assumes name is in the third cell and email is in the fourth cell
      const userName = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
      const userEmail = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
      // Show the row if the name or email includes the search term, else hide
      if (userName.includes(searchTerm) || userEmail.includes(searchTerm)) {
          row.style.display = '';
      } else {
          row.style.display = 'none';
      }
  });
}

// Event listener for the search button
document.querySelector('.filter-button').addEventListener('click', searchUsers);

// Call fetchUsers to load the data when the page is loaded or the script is executed
fetchUsers();