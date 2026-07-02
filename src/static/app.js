document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  let messageTimeout;

  function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    clearTimeout(messageTimeout);
    messageTimeout = setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participants = Array.isArray(details.participants) ? details.participants : [];
        const participantItems = participants.length
          ? participants
              .map(
                (participant) => `
                  <li class="participant-chip">
                    <span class="participant-name">${participant}</span>
                    <button
                      type="button"
                      class="participant-remove"
                      data-activity="${name}"
                      data-email="${participant}"
                      aria-label="Remove ${participant}"
                    >
                      ×
                    </button>
                  </li>
                `
              )
              .join("")
          : '<li class="participant-chip participant-chip--empty">No participants yet.</li>';

        activityCard.innerHTML = `
          <div class="activity-card__header">
            <h4>${name}</h4>
            <span class="activity-card__badge">${spotsLeft} spots left</span>
          </div>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <div class="participants-section">
            <h5>Participants</h5>
            <ul class="participants-list">${participantItems}</ul>
          </div>
        `;

        activityCard.addEventListener("click", async (event) => {
          const removeButton = event.target.closest(".participant-remove");
          if (!removeButton) return;

          const activityName = removeButton.dataset.activity;
          const participantEmail = removeButton.dataset.email;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(participantEmail)}`,
              { method: "DELETE" }
            );
            const result = await response.json();

            if (response.ok) {
              showMessage(result.message, "success");
              await fetchActivities();
            } else {
              showMessage(result.detail || "Unable to remove participant.", "error");
            }
          } catch (error) {
            showMessage("Failed to remove participant. Please try again.", "error");
            console.error("Error removing participant:", error);
          }
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        await fetchActivities();
        signupForm.reset();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
