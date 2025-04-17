<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- App Header -->
    <header class="bg-white shadow-sm py-3 px-4 border-b border-gray-200">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900 flex items-center">
          <i class="pi pi-comments text-amber-500 mr-2"></i>
          Messages
        </h1>
        <button
          class="p-2 rounded-full bg-amber-500 text-white hover:bg-amber-600 transition-colors"
        >
          <i class="pi pi-comments"></i>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden max-w-6xl mx-auto w-full">
      <!-- Chat List -->
      <aside
        class="w-full md:w-80 bg-white border-r border-gray-200 flex flex-col"
        :class="{ 'hidden md:flex': activeChat }"
      >
        <div class="p-3 border-b border-gray-200">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search conversations..."
              class="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-amber-400 focus:border-transparent"
            />
            <i class="pi pi-search absolute left-3 top-2.5 text-gray-400"></i>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto">
          <!-- Loading State -->
          <div v-if="isLoading" class="p-4 text-center text-gray-500">
            Loading chats...
          </div>
          <!-- Error State -->
          <div v-else-if="error" class="p-4 text-center text-red-500">
            {{ error }}
            <button
              @click="fetchChats"
              class="mt-2 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600"
            >
              Retry
            </button>
          </div>
          <!-- Empty State -->
          <div
            v-else-if="!filteredChats.length"
            class="p-4 text-center text-gray-500"
          >
            No chats found. Start a new conversation!
          </div>
          <!-- Chat List -->
          <div
            v-for="chat in filteredChats"
            :key="chat.id"
            @click="openChat(chat.id)"
            class="p-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'bg-amber-50': chat.id === activeChat }"
          >
            <div class="flex items-center space-x-3">
              <div class="relative">
                <div
                  class="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-white font-medium"
                >
                  {{ chat.item_name?.charAt(0)?.toUpperCase() || "?" }}
                </div>
                <span
                  v-if="hasUnreadMessages(chat.id)"
                  class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"
                ></span>
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-baseline">
                  <h3 class="text-sm font-medium text-gray-900 truncate">
                    {{ chat.item_name || "New Chat" }}
                  </h3>
                  <span class="text-xs text-gray-500 whitespace-nowrap ml-2">
                    {{ formatTime(chat.lastMessageTime) }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 truncate">
                  {{ chat.lastMessage || "No messages yet" }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      

      <!-- Chat Window -->
      <div v-if="activeChat" class="flex-1 flex flex-col bg-white">
        <!-- Chat Header -->
        <div class="p-3 border-b border-gray-200 flex items-center">
          <button
            @click="activeChat = null"
            class="md:hidden mr-2 text-gray-500 hover:text-gray-700"
          >
            <i class="pi pi-arrow-left"></i>
          </button>

          <div class="flex items-center flex-1">
            <div
              class="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-white font-medium mr-3"
            >
              {{ getChatInitial(activeChat) }}
            </div>
            <div>
              <h2 class="text-sm font-medium text-gray-900">
                {{ getChatName(activeChat) }}
              </h2>
              <p class="text-xs text-gray-500">
                <span v-if="isOnline(activeChat)" class="flex items-center">
                  <span class="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                  Online
                </span>
                <span v-else> Last seen {{ getLastSeen(activeChat) }} </span>
              </p>
            </div>
          </div>

          <button class="p-2 text-gray-500 hover:text-gray-700 rounded-full">
            <i class="pi pi-ellipsis-v"></i>
          </button>
        </div>

        <!-- Messages -->
        <div
          ref="messagesContainer"
          class="flex-1 p-4 overflow-y-auto bg-gray-50"
        >
          <div
            v-for="message in messages[activeChat]"
            :key="message.id"
            class="flex mb-4"
            :class="message.sentBy === 'me' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-xs md:max-w-md rounded-lg px-4 py-2"
              :class="{
                'bg-white border border-gray-200': message.sentBy !== 'me',
                'bg-amber-500 text-black': message.sentBy === 'me',
              }"
            >
              <p class="text-sm break-words">{{ message.text }}</p>
              <div
                class="flex items-center justify-end mt-1 text-xs"
                :class="{
                  'text-gray-400': message.sentBy !== 'me',
                  'text-amber-100': message.sentBy === 'me',
                }"
              >
                {{ formatTime(message.sent_at) }}
                <i
                  v-if="message.sentBy === 'me'"
                  class="pi ml-1"
                  :class="{
                    'pi-check': !message.read,
                    'pi-check-double text-blue-300': message.read,
                  }"
                ></i>
              </div>
            </div>
          </div>
        </div>

       

        <!-- Message Input -->
        <div class="p-3 border-t border-gray-200 bg-white">
          <div class="flex items-center space-x-2">
            <button class="p-2 text-gray-500 hover:text-amber-500">
              <i class="pi pi-paperclip"></i>
            </button>
            <input
              v-model="newMessage"
              @keyup.enter="sendMessage"
              type="text"
              placeholder="Type a message..."
              class="flex-1 px-4 py-2 bg-gray-100 rounded-full focus:ring-2 focus:ring-amber-400 focus:border-transparent outline-none"
            />
            <button
              @click="sendMessage"
              :disabled="!newMessage.trim()"
              class="p-2 bg-amber-500 text-white rounded-full hover:bg-amber-600 disabled:opacity-50"
            >
              <i class="pi pi-send"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="!activeChat && isDesktop"
        class="hidden md:flex flex-1 items-center justify-center bg-gray-50"
      >
        <div class="text-center p-6 max-w-md">
          <i class="pi pi-box text-5xl text-gray-300 mb-4"></i>
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            Search for an Item
          </h3>
          <p class="text-gray-500 mb-4">
            Choose on the item details page click on talk to owner to start a
            conversation.
          </p>
          <RouterLink
            to="/categories"
            class="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600"
          >
            Search for Item
          </RouterLink>
        </div>
      </div>
      <div v-if="chatStore.chatState.chatId"
              class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <div class="bg-white rounded-lg shadow-lg p-6 w-96">
                <h2 class="text-lg font-bold text-gray-800 mb-4">Review Your Message</h2>
                <img :src="chatStore.chatState.equipmentImage" alt="Equipment Image"
                  class="w-full h-40 object-cover rounded-lg mb-4" />

                <!-- Editable Message -->
                <textarea v-model="chatStore.chatState.initialMessage"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4" rows="4"
                  placeholder="Edit your message here">{{
                    chatStore.chatState.initialMessage }}</textarea>

                <div class="flex justify-end space-x-3">
                  <button @click="chatStore.chatState.chatId = null"
                    class="px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg">
                    Cancel
                  </button>
                  <button @click="chatStore.sendMessageAndReset"
                    class="px-4 py-2 bg-[#ffc107] hover:bg-[#ffd740] text-gray-800 rounded-lg">
                    Send
                  </button>
                </div>
              </div>
            </div>

    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "@/store/auth";
import { useChatStore } from "@/store/chat";

const authStore = useAuthStore();
const chatStore = useChatStore();

const api_base_url = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Data
const chats = ref([]);
const messages = reactive({});
const activeChat = ref(null);
const newMessage = ref("");
const messagesContainer = ref(null);
const isLoading = ref(false);
const error = ref(null);
const searchQuery = ref("");

// Computed
const isDesktop = computed(() => window.innerWidth >= 768);

const filteredChats = computed(() => {
  if (!searchQuery.value.trim()) return chats.value;
  return chats.value.filter(
    (chat) =>
      chat.item_name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      chat.name?.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Methods
const fetchChats = async () => {
  if (!authStore.user) {
    error.value = "Please log in to view chats.";
    return;
  }
  isLoading.value = true;
  error.value = null;
  try {
    const response = await axios.get(`${api_base_url}/api/accounts/chats/`, {
      withCredentials: true,
    });
    console.log("Fetched chats:", response.data); // Debug log
    chats.value = response.data.map((chat) => {
      const otherParticipant = chat.participants.find(
        (p) => p.id !== authStore.user?.id
      );
      const lastMessage = chat.messages[chat.messages.length - 1];
      return {
        id: chat.id,
        name: otherParticipant?.username || "Unknown",
        lastMessage: lastMessage?.content || "No messages yet",
        lastMessageTime: lastMessage?.sent_at || chat.created_at,
        created_at: chat.created_at,
        participants: chat.participants,
        item_name: chat.item_name,
        otherParticipant,
      };
    });
    if (!chats.value.length) {
      console.log("No chats found for user:", authStore.user.id);
    }
  } catch (err) {
    console.error("Error fetching chats:", err);
    error.value =
      err.response?.data?.detail ||
      "Failed to load chats. Please try again later.";
  } finally {
    isLoading.value = false;
  }
};

const fetchMessages = async (chatId) => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await axios.get(
      `${api_base_url}/api/accounts/chats/${chatId}/`,
      { withCredentials: true }
    );
    console.log("Fetched messages for chat", chatId, ":", response.data.messages); // Debug log
    messages[chatId] = response.data.messages.map((msg) => ({
      id: msg.id,
      text: msg.content,
      sentBy: msg.sender === authStore.user?.id ? "me" : "them",
      sent_at: msg.sent_at,
      read: msg.read,
    }));
    activeChat.value = chatId;
    nextTick(() => scrollToBottom());
  } catch (err) {
    console.error("Error fetching messages:", err);
    error.value =
      err.response?.data?.detail ||
      "Failed to load messages. Please try again.";
  } finally {
    isLoading.value = false;
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim()) return;
  try {
    await axios.post(
      `${api_base_url}/api/accounts/messages/`,
      {
        content: newMessage.value,
        chat: activeChat.value,
        receiver: getReceiverId(activeChat.value),
      },
      { withCredentials: true }
    );
    await fetchMessages(activeChat.value);
    newMessage.value = "";
    await fetchChats();
  } catch (error) {
    console.error("Error sending message:", error);
    error.value = "Failed to send message. Please try again.";
  }
};

const openChat = (chatId) => {
  if (!messages[chatId]) {
    fetchMessages(chatId);
  } else {
    activeChat.value = chatId;
    nextTick(() => scrollToBottom());
  }
};



const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const getReceiverId = (chatId) => {
  const chat = chats.value.find((c) => c.id === chatId);
  return chat?.participants.find((p) => p.id !== authStore.user?.id)?.id;
};

const getChatName = (chatId) => {
  const chat = chats.value.find((c) => c.id === chatId);
  return chat?.item_name || chat?.name || "Unnamed Chat";
};

const getChatInitial = (chatId) => {
  const chat = chats.value.find((c) => c.id === chatId);
  return chat?.item_name?.charAt(0)?.toUpperCase() || "?";
};

const hasUnreadMessages = (chatId) => {
  if (!messages[chatId]) return false;
  return messages[chatId].some((msg) => msg.sentBy === "them" && !msg.read);
};

const isOnline = (chatId) => {
  const chat = chats.value.find((c) => c.id === chatId);
  // Mock implementation - replace with real online status check
  return chat?.otherParticipant?.id % 2 === 0;
};

const getLastSeen = (chatId) => {
  const chat = chats.value.find(c => c.id === chatId);
  
  // If no participant data exists
  if (!chat?.otherParticipant?.last_seen) {
    return 'recently'; // or 'unknown' or whatever default you prefer
  }
  
  // If you have actual last_seen data from your API
  const lastSeenDate = new Date(chat.otherParticipant.last_seen);
  const now = new Date();
  const hoursAgo = Math.floor((now - lastSeenDate) / (1000 * 60 * 60));
  
  if (hoursAgo < 1) return 'recently';
  if (hoursAgo < 24) return `${hoursAgo}h ago`;
  
  const daysAgo = Math.floor(hoursAgo / 24);
  return `${daysAgo}d ago`;
};

const formatTime = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

// Lifecycle
onMounted(() => {
  fetchChats();
  window.addEventListener("resize", () => {
    if (activeChat.value) {
      nextTick(() => scrollToBottom());
    }
  });
});
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Smooth transitions */
.message-enter-active {
  transition: all 0.3s ease;
}
.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
</style>