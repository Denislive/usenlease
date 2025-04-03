import { defineStore } from 'pinia';
import { ref, reactive, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification';
import { useRouter } from 'vue-router';

export const useChatStore = defineStore('chat', () => {
  // Dependencies
  const authStore = useAuthStore();
  const { showNotification } = useNotifications();
  const router = useRouter();

  // Configuration
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  if (!api_base_url) {
    console.error('API base URL is not configured');
    showNotification('Error', 'Application configuration error', 'error');
  }

  // State
  const chats = ref([]);
  const messages = reactive({});
  const activeChat = ref(null);
  const newMessage = ref('');
  const isLoading = ref(false);
  
  // State for chat creation
  const chatState = ref({
    chatId: null,
    equipmentImage: null,
    initialMessage: '',
    equipmentOwner: null,
    equipmentDetails: null,
    item_name: ''
  });

  // Getters
  const activeChatMessages = computed(() => {
    return activeChat.value ? messages[activeChat.value] || [] : [];
  });

  const otherParticipant = computed(() => {
    if (!activeChat.value) return null;
    const chat = chats.value.find(c => c.id === activeChat.value);
    return chat?.participants?.find(p => p.id !== authStore.user?.id);
  });

  // Actions
  const fetchChats = async () => {
    if (!authStore.isAuthenticated) return;
    
    isLoading.value = true;
    try {
      const response = await secureAxios.get(`${api_base_url}/api/accounts/chats/`);
      
      chats.value = response.data.map(chat => {
        const otherUser = chat.participants.find(
          p => p.id !== authStore.user.id
        );
        
        return {
          id: chat.id,
          name: otherUser?.username || 'Unknown',
          lastMessage: chat.messages[chat.messages.length - 1]?.content || 'No messages yet',
          created_at: chat.created_at,
          participants: chat.participants,
          item_name: chat.item_name,
          unreadCount: chat.unread_count || 0
        };
      });
    } catch (error) {
      handleError(error, 'Failed to fetch chats');
    } finally {
      isLoading.value = false;
    }
  };

  const fetchMessages = async (chatId) => {
    if (!chatId) return;
    
    isLoading.value = true;
    try {
      const response = await secureAxios.get(
        `${api_base_url}/api/accounts/chats/${chatId}/`
      );

      messages[chatId] = response.data.messages.map(msg => ({
        id: msg.id,
        text: msg.content,
        sentBy: msg.sender === authStore.user.id ? 'me' : 'them',
        sent_at: msg.sent_at,
        sender: msg.sender,
        isRead: msg.is_read
      }));
      
      activeChat.value = chatId;
      markMessagesAsRead(chatId);
    } catch (error) {
      handleError(error, `Failed to load messages for chat ID: ${chatId}`);
    } finally {
      isLoading.value = false;
    }
  };

  const sendMessage = async () => {
    const messageContent = newMessage.value.trim();
    if (!messageContent || !activeChat.value) return;

    try {
      await secureAxios.post(`${api_base_url}/api/accounts/messages/`, {
        content: messageContent,
        chat: activeChat.value,
        receiver: getReceiverId(activeChat.value)
      });

      await fetchMessages(activeChat.value);
      newMessage.value = '';
    } catch (error) {
      handleError(error, 'Failed to send the message');
    }
  };

  const createChat = async (equipmentOwner, equipmentDetails) => {
    if (!authStore.isAuthenticated) {
      showNotification(
        'Authentication Required',
        'Please log in to start a chat!',
        'error'
      );
      return;
    }

    isLoading.value = true;
    try {
      const response = await secureAxios.post(
        `${api_base_url}/api/accounts/chats/`,
        {
          participants: [equipmentOwner],
          item_name: equipmentDetails.name,
          item_image_url: equipmentDetails.images[0]?.image_url
        }
      );

      chatState.value = {
        chatId: response.data.id,
        equipmentImage: equipmentDetails.images[0]?.image_url,
        initialMessage: `Hello, I am interested in renting the ${equipmentDetails.name}. Could you please provide more details?`,
        equipmentOwner,
        equipmentDetails,
        item_name: equipmentDetails.name
      };

      showNotification(
        'Chat Created',
        'Chat created successfully! Review the message before sending.',
        'success'
      );
    } catch (error) {
      if (error.response?.status === 409) {
        // Chat already exists
        const existingChatId = error.response.data.chat_id;
        chatState.value.chatId = existingChatId;
        showNotification(
          'Chat Found',
          'You already have a chat about this item',
          'info'
        );
      } else {
        handleError(error, 'Failed to create chat');
      }
    } finally {
      isLoading.value = false;
    }
  };

  const sendMessageAndReset = async () => {
    if (!chatState.value.chatId) return;

    try {
      await secureAxios.post(`${api_base_url}/api/accounts/messages/`, {
        content: chatState.value.initialMessage,
        chat: chatState.value.chatId,
        receiver: chatState.value.equipmentOwner,
        item_image_url: chatState.value.equipmentImage
      });

      showNotification(
        'Message Sent',
        'Your message was sent successfully!',
        'success'
      );
      
      // Open the chat after sending
      await fetchMessages(chatState.value.chatId);
      resetChatState();
    } catch (error) {
      handleError(error, 'Failed to send initial message');
    }
  };

  // Helper functions
  const getReceiverId = (chatId) => {
    const chat = chats.value.find(c => c.id === chatId);
    return chat?.participants?.find(p => p.id !== authStore.user.id)?.id;
  };

  const markMessagesAsRead = async (chatId) => {
    try {
      await secureAxios.patch(
        `${api_base_url}/api/accounts/chats/${chatId}/mark-read/`
      );
      // Update local state to reflect read status
      if (messages[chatId]) {
        messages[chatId].forEach(msg => {
          if (msg.sentBy === 'them') msg.isRead = true;
        });
      }
    } catch (error) {
      console.error('Failed to mark messages as read:', error);
    }
  };

  const resetChatState = () => {
    chatState.value = {
      chatId: null,
      equipmentImage: null,
      initialMessage: '',
      equipmentOwner: null,
      equipmentDetails: null,
      item_name: ''
    };
  };

  const handleError = (error, defaultMessage) => {
    const message = error.response?.data?.detail || 
                    error.response?.data?.message || 
                    defaultMessage;
    showNotification('Error', message, 'error');
    console.error(error);
  };

  // Secure axios instance with interceptors
  const secureAxios = axios.create({
    withCredentials: true
  });

  secureAxios.interceptors.request.use(config => {
    if (authStore.isAuthenticated && authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  }, error => {
    return Promise.reject(error);
  });

  secureAxios.interceptors.response.use(response => {
    return response;
  }, error => {
    if (error.response?.status === 401) {
      authStore.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  });

  return {
    // State
    chats,
    messages,
    activeChat,
    newMessage,
    chatState,
    isLoading,
    
    // Getters
    activeChatMessages,
    otherParticipant,
    
    // Actions
    fetchChats,
    fetchMessages,
    sendMessage,
    openChat: fetchMessages, // Alias for consistency
    createChat,
    sendMessageAndReset,
    resetChatState
  };
});