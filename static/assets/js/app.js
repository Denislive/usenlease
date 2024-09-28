    // Handle mobile nav item clicks
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
        item.addEventListener('click', function () {
            // Remove active class from all items
            document.querySelectorAll('.mobile-nav-item').forEach(nav => {
                nav.classList.remove('active');
            });

            // Add active class to the clicked item
            this.classList.add('active');

            const section = this.getAttribute('data-section');

            // Get the content from the selected section
            const content = document.getElementById(section).innerHTML;

            // Set modal content
            document.getElementById('modal-content').innerHTML = content;

            // Initialize the accordion before opening the modal
            $('#modal-content').find('.accordion').foundation(); // Initialize accordions in the modal content

            // Open the modal
            $('#modal').foundation('open'); // Use Foundation's method to open the modal
        });
    });


    

$(document).foundation()


// Toggle footer content visibility on small devices
$('#footerToggle').on('click', function() {
  $('#footerContent').toggleClass('hidden');
  var isHidden = $('#footerContent').hasClass('hidden');
  $(this).toggleClass('bi-chevron-down bi-chevron-up');
  $(this).attr('title', isHidden ? 'Show Footer' : 'Hide Footer');
});




  document.addEventListener('DOMContentLoaded', function() {
    const thumbnails = document.querySelectorAll('.thumbnail-list img');
    const mainImage = document.getElementById('mainImage');
    const thumbnailList = document.getElementById('thumbnailList');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');

    let currentIndex = 0;

    function updateMainImage(src) {
        mainImage.src = src;
    }

    function updateSlider() {
        const offset = -currentIndex * (100 + 10); // 100px width + 10px margin
        thumbnailList.style.transform = `translateX(${offset}px)`;
    }

    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', function() {
            const largeImageSrc = this.getAttribute('data-large');
            updateMainImage(largeImageSrc);
        });
    });

    prevButton.addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlider();
            const src = thumbnails[currentIndex].getAttribute('data-large');
            updateMainImage(src);
        }
    });

    nextButton.addEventListener('click', function() {
        if (currentIndex < thumbnails.length - 1) {
            currentIndex++;
            updateSlider();
            const src = thumbnails[currentIndex].getAttribute('data-large');
            updateMainImage(src);
        }
    });
});




document.addEventListener('DOMContentLoaded', function() {
  // Example reviews with ratings
  const reviews = [
    { text: "Great product! I really enjoyed using it and would recommend it to others.", rating: 4.5 },
    { text: "The product is decent but has room for improvement.", rating: 3.0 }
  ];

  const reviewsList = document.querySelector('.reviews-list');

  function renderStars(container, rating) {
    const stars = container.querySelectorAll('.star');
    stars.forEach(star => {
      const value = parseFloat(star.getAttribute('data-value'));
      if (value <= rating) {
        star.classList.add('filled');
      } else if (value - 0.5 < rating && value > rating) {
        star.classList.add('half-filled');
      } else {
        star.classList.remove('filled', 'half-filled');
      }
    });
  }

  reviews.forEach(review => {
    const reviewDiv = document.createElement('div');
    reviewDiv.classList.add('review');
    reviewDiv.innerHTML = `<p>${review.text}</p>`;

    // Create stars element for review rating
    const starsDiv = document.createElement('div');
    starsDiv.classList.add('rating-stars');
    reviewDiv.appendChild(starsDiv);

    for (let i = 1; i <= 5; i++) {
      const star = document.createElement('span');
      star.classList.add('star');
      star.setAttribute('data-value', i);
      star.innerHTML = '&#9733;';
      starsDiv.appendChild(star);
    }

    renderStars(starsDiv, review.rating);
    reviewsList.appendChild(reviewDiv);
  });

  // User rating functionality
  const starElements = document.querySelectorAll('#userRating .star');
  const hiddenRatingInput = document.getElementById('hidden-rating');

  starElements.forEach(star => {
    star.addEventListener('mouseover', function() {
      const value = parseFloat(star.getAttribute('data-value'));
      starElements.forEach(s => s.classList.toggle('hovered', parseFloat(s.getAttribute('data-value')) <= value));
    });

    star.addEventListener('mouseout', function() {
      starElements.forEach(s => s.classList.remove('hovered'));
    });

    star.addEventListener('click', function() {
      const value = parseFloat(star.getAttribute('data-value'));
      hiddenRatingInput.value = value;
      starElements.forEach(s => s.classList.toggle('filled', parseFloat(s.getAttribute('data-value')) <= value));
      starElements.forEach(s => s.classList.remove('hovered'));
    });
  });
});



document.addEventListener('DOMContentLoaded', function() {
  const navItems = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.section-content');

  // Function to switch active section
  function activateSection(sectionId) {
      sections.forEach(section => {
          section.classList.remove('active');
      });

      document.getElementById(sectionId).classList.add('active');
  }

  // Add click event listeners to each nav item
  navItems.forEach(item => {
      item.addEventListener('click', function() {
          navItems.forEach(nav => nav.classList.remove('active'));
          this.classList.add('active');
          activateSection(this.getAttribute('data-section'));
      });
  });

  // Initialize the first active section
  const initialActiveItem = document.querySelector('.nav-item.active');
  if (initialActiveItem) {
      activateSection(initialActiveItem.getAttribute('data-section'));
  }
});





document.querySelectorAll('.favorite-button').forEach(button => {
  button.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent the default action
      this.classList.toggle('active');
  });
});






let locationData = {}; // Global variable to store the location data

// Load CSV data and parse it
async function loadCSV() {
    try {
        const response = await fetch('http://127.0.0.1:8000/static/assets/data/usa.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.text();
        const rows = data.split('\n').slice(1); // Skip header
        const parsedData = {};

        rows.forEach(row => {
            const [state, cities] = row.split(/,(.+)/); // Split on the first comma
            if (state && cities) {
                const cityList = cities.replace(/"/g, '').split(',').map(city => city.trim());
                parsedData[state] = { 
                    count: cityList.length, 
                    cities: cityList.reduce((acc, city) => {
                        acc[city] = 1; // Count of 1 for each city
                        return acc;
                    }, {})
                };
            }
        });

        locationData = parsedData; // Store parsed data globally
        populateStates(); // Populate states after loading data
    } catch (error) {
        console.error('Error loading CSV:', error);
        alert('Failed to load location data. Please try again later.'); // User feedback
    }
}

// Populate states list on modal open
function populateStates() {
    const statesList = document.getElementById('statesList');
    statesList.innerHTML = '';
    const sortedStates = Object.keys(locationData).sort(); // Sort states alphabetically

    sortedStates.forEach(state => {
        const li = document.createElement('li');
        li.className = 'cell'; // Add Foundation grid class
        li.innerHTML = `<a href="#" onclick="selectState('${state}')">${state} (${locationData[state].count})</a>`;
        statesList.appendChild(li);
    });
}

// Select a state and show cities
function selectState(state) {
    document.getElementById('selectedStateName').textContent = state;
    document.getElementById('state-selection').style.display = 'none';
    document.getElementById('city-selection').style.display = 'block';
    displayCities(state); // Show cities for the selected state
    updateLocationButton(state); // Update the button with the selected state
    document.getElementById('cityModalSearchInput').value = ''; // Clear any previous input
    filterCityLocations(); // Show all cities initially
}

// Display cities based on selected state
function displayCities(state) {
    const citiesList = document.getElementById('citiesList');
    citiesList.innerHTML = ''; // Clear previous list
    const citiesToShow = Object.keys(locationData[state].cities).sort(); // Sort cities alphabetically

    citiesToShow.forEach(city => {
        const li = document.createElement('li');
        li.className = 'cell';
        li.innerHTML = `<a href="#" onclick="handleCitySelection('${state}', '${city}')">${city} (${locationData[state].cities[city]})</a>`;
        citiesList.appendChild(li);
    });
}

// Handle city selection
function handleCitySelection(state, city) {
  document.getElementById('selectedStateName').textContent = `${city}, ${state}`;
  updateLocationButton(`${city}, ${state}`); // Update button with selected city

  // Close the modal using Foundation
  const modal = document.getElementById('usaLocationModal');
  $(modal).foundation('close'); // Use Foundation's method to close the modal

  // Alternatively, if not using Foundation, you can hide it directly
  // modal.style.display = 'none'; 
}

// Update the button text
function updateLocationButton(location) {
    const allButton = document.getElementById('allButton');
    allButton.textContent = `All in ${location}`; // Update button text
}

// Function to filter states and cities based on modal search input
function filterModalLocations() {
    const input = document.getElementById('modalSearchInput').value.toLowerCase();
    const statesList = document.getElementById('statesList');
    statesList.innerHTML = '';

    // Filter states
    Object.keys(locationData).sort().forEach(state => {
        if (state.toLowerCase().includes(input)) {
            const li = document.createElement('li');
            li.className = 'cell'; // Add Foundation grid class
            li.innerHTML = `<a href="#" onclick="selectState('${state}')">${state} (${locationData[state].count})</a>`;
            statesList.appendChild(li);
        }
        
        // Filter cities within the state
        const cities = locationData[state].cities;
        Object.keys(cities).forEach(city => {
            if (city.toLowerCase().includes(input)) {
                const li = document.createElement('li');
                li.className = 'cell'; // Add Foundation grid class
                li.innerHTML = `<a href="#" onclick="handleCitySelection('${state}', '${city}')">${state} > ${city} (${cities[city]})</a>`;
                statesList.appendChild(li);
            }
        });
    });
}

// Event listener for the back to states button in the city selection
document.getElementById('backToStates').onclick = () => {
  document.getElementById('state-selection').style.display = 'block';
  document.getElementById('city-selection').style.display = 'none';
  document.getElementById('cityModalSearchInput').value = ''; // Clear city search input
};

// Add event listeners for filtering
document.getElementById('modalSearchInput').addEventListener('input', filterModalLocations);
document.getElementById('cityModalSearchInput').addEventListener('input', filterCityLocations);

// Filter city locations based on search input
function filterCityLocations() {
    const input = document.getElementById('cityModalSearchInput').value.toLowerCase().trim(); // Get input and trim whitespace
    const citiesList = document.getElementById('citiesList');
    const selectedState = document.getElementById('selectedStateName').textContent; // Get the current state

    citiesList.innerHTML = ''; // Clear previous list

    // Check if the selected state exists in locationData
    if (locationData[selectedState]) {
        const citiesToShow = Object.keys(locationData[selectedState].cities); // Get cities for selected state

        // Filter cities based on input
        const filteredCities = citiesToShow.filter(city => city.toLowerCase().includes(input));

        // Check if any cities were found
        if (filteredCities.length > 0) {
            // Display filtered cities
            filteredCities.forEach(city => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="#" onclick="handleCitySelection('${selectedState}', '${city}')">${city} (${locationData[selectedState].cities[city]})</a>`;
                citiesList.appendChild(li);
            });
        } else {
            // Show a message if no cities match the search
            const li = document.createElement('li');
            li.textContent = 'No cities found';
            citiesList.appendChild(li);
        }
    } else {
        // Optionally handle the case where the selected state is invalid
        const li = document.createElement('li');
        li.textContent = 'Invalid state selected';
        citiesList.appendChild(li);
    }
}

// Call loadCSV when the document is ready
document.addEventListener('DOMContentLoaded', loadCSV);




