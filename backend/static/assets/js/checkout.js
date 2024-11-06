// Initialize Stripe with the public key passed from Django template
console.log("Initializing Stripe with public key:", stripePublicKey);
const stripe = Stripe(stripePublicKey);

// Fetch the CSRF token from the meta tag
const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
console.log("CSRF Token fetched:", csrftoken);

let elements;

initialize();
checkStatus();

document
  .querySelector("#payment-form")
  .addEventListener("submit", handleSubmit);

// Fetches a payment intent and captures the client secret
async function initialize() {
  console.log("Initializing payment intent...");

  try {
    const response = await fetch(createPaymentUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
    });

    if (!response.ok) {
      console.error("Error in fetch response:", response.status, response.statusText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Response from createPaymentUrl:", data);

    const { clientSecret } = data;
    console.log("Client Secret received:", clientSecret);

    const appearance = {
      theme: 'stripe',
    };
    elements = stripe.elements({ appearance, clientSecret });

    // Initialize Address Element
    const addressElement = elements.create("address", {
      mode: "shipping",
      autocomplete: {
        mode: "google_maps_api",
        apiKey: "YOUR_GOOGLE_MAPS_API_KEY",  // Replace with your actual Google Maps API key
      },
      allowedCountries: ['US'],
      blockPoBox: true,
      fields: {
        phone: 'always',
      },
      validation: {
        phone: {
          required: 'never',
        },
      },
    });

    addressElement.mount("#address-element");

    addressElement.on('change', (event) => {
      if (event.complete) {
        const address = event.value.address;
        console.log("Address captured:", address);
      }
    });

    const paymentElementOptions = {
      layout: "tabs",
    };

    const paymentElement = elements.create("payment", paymentElementOptions);
    paymentElement.mount("#payment-element");
    console.log("Payment element mounted successfully.");

  } catch (error) {
    console.error("Error in initialize function:", error);
    showMessage("An error occurred while initializing payment.");
  }
}

async function handleSubmit(e) {
  e.preventDefault();
  console.log("Payment form submitted.");
  setLoading(true);

  try {
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/success/`,  // Dynamic URL handling
        receipt_email: document.getElementById("email").value,
      },
    });

    if (error) {
      console.error("Error in stripe.confirmPayment:", error);
      if (error.type === "card_error" || error.type === "validation_error") {
        showMessage(error.message);
      } else {
        showMessage("An unexpected error occurred.");
      }
    } else {
      console.log("Payment confirmation successful.");
    }

  } catch (error) {
    console.error("Error in handleSubmit function:", error);
    showMessage("An error occurred during payment submission.");
  }

  setLoading(false);
}

// Fetches the payment intent status after payment submission
async function checkStatus() {
  console.log("Checking payment status...");
  const clientSecret = new URLSearchParams(window.location.search).get(
    "payment_intent_client_secret"
  );

  if (!clientSecret) {
    console.log("No client secret found in URL.");
    return;
  }

  try {
    const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);
    console.log("Payment Intent status:", paymentIntent.status);

    switch (paymentIntent.status) {
      case "succeeded":
        showMessage("Payment succeeded!");
        break;
      case "processing":
        showMessage("Your payment is processing.");
        break;
      case "requires_payment_method":
        showMessage("Your payment was not successful, please try again.");
        break;
      default:
        showMessage("Something went wrong.");
        break;
    }
  } catch (error) {
    console.error("Error in checkStatus function:", error);
    showMessage("An error occurred while checking payment status.");
  }
}

// ------- UI helpers -------

function showMessage(messageText) {
  const messageContainer = document.querySelector("#payment-message");
  console.log("Showing message:", messageText);

  messageContainer.classList.remove("hidden");
  messageContainer.textContent = messageText;

  setTimeout(function () {
    messageContainer.classList.add("hidden");
    messageContainer.textContent = "";
  }, 4000);
}

// Show a spinner on payment submission
function setLoading(isLoading) {
  console.log("Setting loading state:", isLoading);
  if (isLoading) {
    // Disable the button and show a spinner
    document.querySelector("#submit").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
  } else {
    document.querySelector("#submit").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  }
}
