import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification';
import { useRouter } from 'vue-router';

export const useChatStore = defineStore('chat', () => {
  const authStore = useAuthStore();
  const { showNotification } = useNotifications();

  const router = useRouter();

  // State
  const chats = ref([]); // List of all chats
  const messages = reactive({}); // Messages for each chat, keyed by chat ID
  const activeChat = ref(null); // Currently open chat ID
  const newMessage = ref(""); // Message being typed
  const lastMessage = ref("");
  const api_base_url = import.meta.env.VITE_API_BASE_URL;

// Fetch the list of chats for the logged-in user
const fetchChats = async () => {
  try {
    console.log("Fetching chats");
    
    const response = await axios.get(`${api_base_url}/api/accounts/chats/`, {
      withCredentials: true,
    });

    // Transform chat data and store it
    chats.value = response.data.map((chat) => {
      const otherParticipant = chat.participants.find(
        (participant) => participant.id !== authStore.user.id
      );

      const lastMessage = chat.messages.length
        ? chat.messages[chat.messages.length - 1].content
        : "No messages yet";

      // Log the last message for this chat
      console.log(`Chat ID: ${chat.id}, Last Message: ${lastMessage}`);

      return {
        id: chat.id,
        name: otherParticipant?.username || "Unknown", // Default to "Unknown" if participant is not found
        lastMessage: lastMessage,
        created_at: chat.created_at,
        participants: chat.participants,
        item_name: chat.item_name,

      };
    });
  } catch (error) {
    showNotification("Error", "Failed to fetch chats", "error");
  }
};

  // Fetch messages for a specific chat
  const fetchMessages = async (chatId) => {
    try {
      const response = await axios.get(`${api_base_url}/api/accounts/chats/${chatId}/`, {
        withCredentials: true,
      });

      // Store the messages for the selected chat
      messages[chatId] = response.data.messages.map((msg) => ({
        id: msg.id,
        text: msg.content,
        sentBy: msg.sender === authStore.user.id ? "me" : "them", // Determine if the message was sent by the current user or the other participant
        sent_at: msg.sent_at,
        sender: msg.sender,
      }));
      activeChat.value = chatId; // Set the active chat ID
    } catch (error) {
      showNotification('Error', `Failed to load messages for chat ID: ${chatId}`, 'error');
    }
  };

  // Send a new message to the active chat
  const sendMessage = async () => {
    if (!newMessage.value.trim()) return; // Don't send empty messages

    try {
      await axios.post(
        `${api_base_url}/api/accounts/messages/`,
        {
          content: newMessage.value,
          chat: activeChat.value, // Send message to the currently active chat
          receiver: getReceiverId(activeChat.value), // Get the receiver's ID for the current chat
        },
        { withCredentials: true }
      );

      // After sending, fetch updated messages for the active chat
      fetchMessages(activeChat.value);
      newMessage.value = ""; // Clear the input field
    } catch (error) {
      showNotification('Error', 'Failed to send the message', 'error');
    }
  };

  // Open an existing chat and fetch its messages
  const openChat = (chatId) => {
    if (!messages[chatId]) {
      fetchMessages(chatId); // Fetch messages if they haven't been fetched yet
    } else {
      activeChat.value = chatId; // Set the active chat if messages are already loaded
    }
  };

  // Get the receiver's ID for a specific chat (used when sending messages)
  const getReceiverId = (chatId) => {
    const chat = chats.value.find((c) => c.id === chatId);
    const receiver = chat.participants.find(
      (participant) => participant.id !== authStore.user.id
    );

    return receiver?.id;
  };

// Function to clear chat state
const clearChatState = () => {
  chatState.value.chatId = null;
};

const sendMessageAndReset = async () => {
  try {
    // Ensure the equipment image URL is included
    const equipmentImageUrl = chatState.value.equipmentImage; // Get the equipment image URL from state

    // Make the API request to send the message
    await axios.post(
      `${api_base_url}/api/accounts/messages/`,
      {
        content: chatState.value.initialMessage, // Use the updated message
        chat: chatState.value.chatId,
        receiver: chatState.value.equipmentOwner,
        item_image_url: equipmentImageUrl, // Include the equipment image URL
      },
      {
        withCredentials: true,
      }
    );

    // Show success notification
    showNotification(
      "Message Sent",
      "Your message was sent successfully!",
      "success"
    );
    
    clearChatState(); // Reset chatState to null

  } catch (error) {

    // Show error notification
    showNotification(
      "Message Error",
      `Error: ${error.response?.data.detail || error.message}`,
      "error"
    );
  }
};


  const createChat = async (equipmentOwner, equipmentDetails) => {
    const authStore = useAuthStore();
  
    if (authStore.isAuthenticated) {
      try {
        // Step 1: Create a new chat
        const response = await axios.post(
          `${api_base_url}/api/accounts/chats/`,
          {
            participants: [equipmentOwner],
            item_name: equipmentDetails.name, // Include item name in request payload

          },
          {
            withCredentials: true,
          }
        );
  
        console.log("Chat created:", response.data);
  
        // Step 2: Store chat data for user review
        const chatId = response.data.id;
        const initialMessage = ref(`Hello, I am interested in renting the ${equipmentDetails.name}. Could you please provide more details?`);
        chatState.value = {
          chatId,
          equipmentImage: equipmentDetails.images[0].image_url, // Add equipment image
          initialMessage,
          equipmentOwner,
          equipmentDetails,
          item_name: equipmentDetails.name,

        };
  
        showNotification(
          "Chat Created",
          "Chat created successfully! Review the message before sending.",
          "info"
        );
      } catch (error) {
        showNotification(
          "Chat Found!",
          `Info: ${
            error?.response?.data?.message || 
            error?.response?.data?.error || 
            error?.response?.data || 
            error?.message || 
            error?.statusText || 
            error?.toString?.() || 
            "An unknown error occurred."
          }`,
          "Info"
        );
        
      }
    } else {
      showNotification(
        "Authentication Required",
        "Please log in to start a chat!",
        "error"
      );
    }
  };
  
  // State to store chat details for review
  const chatState = ref({
    chatId: null,
    equipmentImage: null,
    initialMessage: "",
    equipmentOwner: null,
    equipmentDetails: null,
    item_name: "",

  });
  
  

  return {
    chats,
    chatState,
    messages,
    lastMessage,
    activeChat,
    newMessage,
    fetchChats,
    fetchMessages,
    sendMessage,
    sendMessageAndReset,
    clearChatState,
    openChat,
    createChat,
  };
});
