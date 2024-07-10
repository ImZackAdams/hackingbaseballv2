document.addEventListener("DOMContentLoaded", function () {
    // Set current year
    document.getElementById("currentYear").textContent = new Date().getFullYear();
  
    // Stripe integration
    const stripe = Stripe("pk_test_51PG1mPIiIqA6x4U9lNczLfuXAXj3xq1pL72t17AK0fD6ffaKgteH6GN7pdo9KLjZQSmdEhOxyJLY3SAUv0Rb034V00W5JxNclc");
    document.getElementById("game-selection-form").addEventListener("submit", function (event) {
      event.preventDefault();
      const selectedGames = Array.from(document.querySelectorAll('input[name="game_id"]:checked')).map(function (checkbox) {
        return checkbox.value;
      });
      console.log("Selected Games: ", selectedGames); // Debugging
      if (selectedGames.length > 0) {
        // Send the selected game IDs to the server
        fetch("/create-checkout-session", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ selectedGames: selectedGames }),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Checkout Session Created:", data); // Debugging
            // Redirect to the Stripe Checkout page
            stripe.redirectToCheckout({ sessionId: data.sessionId });
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
          });
      } else {
        alert("Please select at least one game to proceed to checkout.");
      }
    });
  
 // Set current date
const today = new Date();

const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

const formattedDate =
  monthNames[today.getMonth()] + " " +
  today.getDate() + ", " +
  today.getFullYear();

document.getElementById("current-date").innerHTML = formattedDate;

  });

