import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification';

export const useChatStore = defineStore('chat', () => {
  const authStore = useAuthStore();
  const { showNotification } = useNotifications();

  // State
  const chats = ref([]); // List of all chats
  const messages = reactive({}); // Messages for each chat, keyed by chat ID
  const activeChat = ref(null); // Currently open chat ID
  const newMessage = ref(""); // Message being typed
  const api_base_url = import.meta.env.VITE_API_BASE_URL;

  // Fetch the list of chats for the logged-in user
  const fetchChats = async () => {
    try {
      const response = await axios.get(`${api_base_url}/api/accounts/chats/`, {
        withCredentials: true,
      });

      // Transform chat data and store it
      chats.value = response.data.map((chat) => {
        const otherParticipant = chat.participants.find(
          (participant) => participant.id !== authStore.user.id
        );

        return {
          id: chat.id,
          name: otherParticipant?.username || "Unknown", // Default to "Unknown" if participant is not found
          lastMessage: chat.messages.length
            ? chat.messages[chat.messages.length - 1].content
            : "No messages yet",
          created_at: chat.created_at,
          participants: chat.participants,
        };
      });
    } catch (error) {
      console.error("Error fetching chats:", error);
      showNotification('Error', 'Failed to fetch chats', 'error');
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
      console.error("Error fetching messages:", error);
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
      console.error("Error sending message:", error);
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

  // Create a new chat with an equipment owner (or other user)
  const createChat = async (equipmentOwner) => {
    if (authStore.isAuthenticated) {
      try {
        const response = await axios.post(
          `${api_base_url}/api/accounts/chats/`,
          {
            participants: [equipmentOwner], // Include the logged-in user and the equipment owner as participants
          },
          {
            withCredentials: true, // Ensures cookies are sent with the request
          }
        );

        showNotification(
          "Chat Created",
          `Successfully started a chat with the owner!`,
          "success"
        );

        fetchChats(); // Refresh the chat list to include the new chat
      } catch (error) {
        showNotification(
          "Chat Error",
          `Error: ${error.response?.data || error.message}`,
          "error"
        );
      }
    } else {
      showNotification(
        "Authentication Required",
        `Please log in to start a chat!`,
        "error"
      );
    }
  };

  return {
    chats,
    messages,
    activeChat,
    newMessage,
    fetchChats,
    fetchMessages,
    sendMessage,
    openChat,
    createChat,
  };
});
