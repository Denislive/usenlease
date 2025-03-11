<template>
  <div class="grid grid-cols-12 gap-8 md:px-32 py-4">
    <!-- Sidebar -->
    <div class="col-span-12 lg:col-span-3 bg-white p-4 rounded-lg hidden md:block shadow-md">
      <div class="flex items-center space-x-4 mb-6">
        <i class="bi bi-person text-black text-xl"></i>
        <span class="text-xl font-bold">Welcome,
          {{
            authStore.user?.first_name || authStore.user?.email || "John Doe"
          }}</span>
      </div>

      <hr class="my-4" />

      <!-- Other Sections (Dark Gray) -->
      <div v-for="(section, index) in visibleSections" :key="index" :class="{
        'text-white bg-[#1c1c1c]': authStore.activeSection === section.name,
        'text-[#ffc107]': authStore.activeSection !== section.name,
      }" class="nav-item font-semibold py-1 px-3 rounded-md cursor-pointer mb-2 text-sm" :id="section.name"
        @click="navigateToSection(section.name)">
        {{ section.label }}
      </div>
    </div>

    <!-- Sidebar -->
    <div v-if="showSidebar" class="col-span-12 lg:col-span-3 bg-white p-4 rounded-lg shadow-md md:block lg:hidden">
      <div class="flex items-center space-x-4 mb-6">
        <i class="bi bi-person text-black text-xl"></i>
        <span class="text-xl font-bold">
          Welcome,
          {{
            authStore.user?.first_name || authStore.user?.email || "John Doe"
          }}
        </span>
      </div>
      <!-- Logout Option -->
      <button @click="handleLogout" class="w-full px-4 py-2 text-white bg-red-500 hover:text-[#1c1c1c] rounded text-sm">
        Logout
      </button>
      <hr class="my-4" />

      <!-- Other Sections (Dark Gray) -->
      <div v-for="(section, index) in visibleSections" :key="index" :class="{
        'text-white bg-[#1c1c1c]': authStore.activeSection === section.name,
        'text-[#ffc107]': authStore.activeSection !== section.name,
      }" class="nav-item font-semibold py-1 px-3 rounded-md cursor-pointer mb-2 text-sm" :id="section.name"
        @click="navigateToSection(section.name)">
        {{ section.label }}
      </div>
    </div>


    <!-- Main Content Area -->
    <div class="col-span-12 md:col-span-8 lg:col-span-9 bg-white p-6 rounded-lg shadow-md">
      <div v-for="section in sections" :key="section.name" class="space-y-6">
        <div v-show="authStore.activeSection === section.name" class="section-content">
          <h3 class="text-3xl font-semibold text-gray-800 mb-6 border-b border-gray-300 pb-3">
            {{ section.label }}
          </h3>

          <!-- Personal Information Section -->
          <div v-if="authStore.activeSection === 'personal-info'" class="bg-white rounded-lg shadow-lg p-6 space-y-8">
            <!-- Back Button -->
            <button @click="closeSidebar"
              class="flex items-center text-gray-800 rounded-full p-2 transition hover:bg-gray-200">
              <i class="pi pi-arrow-circle-left text-xl mr-2"></i> Back
            </button>

            <!-- Profile Info -->
            <div class="flex items-center justify-center space-x-6">
              <img :src="`${authStore.user.image}`" alt="Profile"
                class="w-20 h-20 rounded-full border-4 border-gray-300 shadow-md" />
              <div>
                <label for="profile-pic" class="block text-sm text-[#ffc107] font-semibold cursor-pointer">
                  {{ authStore.user?.image ? "Change Picture" : "Add Picture" }}
                </label>
                <input id="profile-pic" type="file" accept="image/*" class="hidden" @change="uploadProfilePicture" />
              </div>
              <div>
                <p class="text-lg font-bold text-gray-800">
                  Welcome,
                  {{
                    authStore.user?.first_name ||
                    authStore.user?.email ||
                    "John Doe"
                  }}
                </p>
              </div>
            </div>


            <hr class="border-gray-200" />

            <!-- Personal Information Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <!-- Full Name -->
              <p class="flex items-center text-gray-700">
                <i class="bi bi-person-circle mr-3 text-xl text-gray-500"></i>
                <span><strong>Full Name:</strong> {{ authStore.user?.first_name }}
                  {{ authStore.user?.last_name }}</span>
              </p>

              <!-- Email -->
              <p class="flex items-center text-gray-700">
                <i class="bi bi-envelope mr-3 text-xl text-gray-500"></i>
                <span><strong>Email:</strong> {{ authStore.user?.email }}</span>
              </p>

              <!-- Phone -->
              <p class="flex items-center text-gray-700">
                <i class="bi bi-phone mr-3 text-xl text-gray-500"></i>
                <span>
                  <strong>Phone:</strong>
                  {{ authStore.user?.phone_number || "Not provided" }}
                  <button @click="phoneModalVisible = !phoneModalVisible"
                    class="ml-2 bg-[#1c1c1c] p-1 rounded text-[#ffc107] hover:text-yellow-600">
                    <i class="bi bi-pencil-square"></i>
                    {{
                      authStore.user?.phone_number ? "Edit Phone" : "Add Phone"
                    }}
                  </button>
                </span>
              </p>

              <!-- Role -->
              <p class="flex items-center text-gray-700 hidden md:block">
                <i class="bi bi-envelope mr-3 text-xl text-gray-500"></i>
                <span><strong>Role:</strong> {{ authStore.user?.role }}</span>
              </p>

              <!-- Role Switch -->
              <div class="flex items-center justify-between bg-gray-50 p-4 rounded-lg shadow-md">
                <div class="flex items-center text-gray-700 space-x-3">
                  <i class="bi bi-shield-lock text-xl text-gray-500"></i>
                  <span class="text-sm">
                    <strong>Role:</strong>
                    {{ authStore.user?.role || "Not assigned" }}
                  </span>
                </div>
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-600">Switch to
                    {{
                      authStore.user?.role === "lessor" ? "lessee" : "lessor"
                    }}:</span>
                  <label for="role-toggle" class="inline-flex relative items-center cursor-pointer">
                    <input type="checkbox" id="role-toggle" v-model="authStore.isOn" class="sr-only peer"
                      @change="authStore.updateUserRole()" />
                    <div
                      class="w-11 h-6 bg-gray-200 rounded-full peer-checked:bg-[#ffc107] peer-checked:after:translate-x-5 after:content-[''] after:absolute after:left-0.5 after:top-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white transition-all">
                    </div>
                  </label>
                </div>
              </div>

              <!-- Address Information -->
              <p class="flex items-center text-gray-700">
                <i class="bi bi-building mr-3 text-xl text-gray-500"></i>
                <span><strong>Company Name:</strong>
                  {{
                    authStore.user?.user_address?.company_name || "Not provided"
                  }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-building mr-3 text-xl text-gray-500"></i>
                <span><strong>Address:</strong>
                  {{
                    authStore.user?.user_address?.street_address ||
                    "No address provided"
                  }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-geo-alt mr-3 text-xl text-gray-500"></i>
                <span><strong>City:</strong>
                  {{
                    authStore.user?.user_address?.city || "Not provided"
                  }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-code-slash mr-3 text-xl text-gray-500"></i>
                <span><strong>Zip Code:</strong>
                  {{
                    authStore.user?.user_address?.zip_code || "Not provided"
                  }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-globe mr-3 text-xl text-gray-500"></i>
                <span><strong>Country:</strong>
                  {{
                    authStore.user?.user_address?.country || "Not provided"
                  }}</span>
              </p>
            </div>

            <!-- Edit Address Button -->
            <div class="flex justify-start">
              <button @click="addressModalVisible = !addressModalVisible"
                class="mr-2 text-[#ffc107] bg-[#1c1c1c] rounded p-2 hover:text-yellow-600">
                <i class="bi bi-pencil-square mr-2"></i>
                {{
                  authStore.user?.user_address &&
                    authStore.user?.user_address.id
                    ? "Edit Address"
                    : "Add Address"
                }}
              </button>
            </div>
          </div>

          <div v-if="authStore.activeSection === 'my-equipments' && authStore.user?.role === 'lessor'"
            id="my-equipments">
            <button @click="closeSidebar"
              class="flex items-center text-gray-800 rounded-full p-2 transition hover:bg-gray-200">
              <i class="pi pi-arrow-circle-left text-xl mr-2"></i> Back
            </button>

            <div v-if="store.userEquipments.length > 0">
              <div class="container mx-auto p-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                  <!-- Loop through the filtered equipments -->
                  <div v-for="equipment in store.userEquipments" :key="equipment.id" @click="goToDetail(equipment.id)"
                    class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer">
                    <div class="relative">
                      <!-- Availability Badge -->
                      <span :class="{
                        'bg-green-500': equipment.is_available,
                        'bg-red-500': !equipment.is_available,
                      }"
                        class="absolute top-2 left-2 text-white text-xs font-bold px-2 py-1 rounded flex items-center">
                        <i :class="{
                          'pi pi-check-circle': equipment.is_available,
                          'pi pi-times-circle': !equipment.is_available,
                        }" class="mr-1"></i>
                        {{
                          equipment.is_available ? "Available" : "Unavailable"
                        }}
                      </span>

                      <!-- Equipment Image -->
                      <img v-if="equipment.images.length > 0" :src="`${equipment.images[0].image_url}`"
                        :alt="equipment.images[0].image_url" class="w-full h-48 object-cover" />

                      <!-- Edit Button -->
                      <a v-if="isEditable(equipment.id)" href="#" @click.stop="openEditModal(equipment)"
                        class="absolute bottom-4 right-4 bg-[#1c1c1c] text-white rounded-full h-10 w-10 flex items-center justify-center hover:text-[#ffc107] transition">
                        <i class="pi pi-pencil"></i>
                      </a>
                    </div>

                    <!-- Equipment Details -->
                    <div class="p-4">
                      <h5 class="text-lg font-semibold">
                        {{ equipment.name }}
                      </h5>
                      <p class="text-gray-600">
                        {{ equipment.hourly_rate }} / Day
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Rental Tables -->
                <div class="mt-8">
                  <h2 class="text-2xl font-bold mb-4">Rental Details</h2>
                  <!-- Currently Rented Table -->
                  <h3 class="text-xl font-semibold mb-2">Currently Rented</h3>
                  <table class="w-full border-collapse bg-white shadow-md rounded-lg overflow-hidden">
                    <thead>
                      <tr class="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                        <th class="py-3 px-6 text-left">Equipment</th>
                        <th class="py-3 px-6 text-center">Duration</th>
                        <th class="py-3 px-6 text-center">Total Income</th>
                        <th class="py-3 px-6 text-center">Actions</th>

                      </tr>
                    </thead>
                    <tbody class="text-gray-600 text-sm font-light">
                      <tr v-for="rental in rentedItems" :key="rental.id"
                        class="border-b border-gray-200 hover:bg-gray-100">
                        <td class="py-3 px-6 text-left">
                          ({{ rental.quantity }}) x {{ rental.item.name || 'N/A' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.quantity ? `$${rental.quantity * rental.item.hourly_rate}` : '$0' }}
                        </td>
                        <td class="py-3 px-6 text-center"> <button @click="openReturnModal(rental.id)"
                            class="bg-blue-600 text-white px-4 py-2 rounded mt-2">
                            Confirm Return
                          </button></td>
                      </tr>
                    </tbody>
                  </table>

                  <!-- Return Confirmation Modal -->
                  <ReturnConfirmationModal :showReturnModal="showReturnModal" :orderItemId="selectedOrderItem"
                    @close="closeReturnModal" @confirm="handleReturnConfirmation" />


                  <!-- Awaiting Approval Table -->
                  <h3 class="text-xl font-semibold mb-2">Awaiting Approval</h3>
                  <table class="w-full border-collapse bg-white shadow-md rounded-lg overflow-hidden">
                    <thead>
                      <tr class="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                        <th class="py-3 px-6 text-left">Equipment</th>
                        <th class="py-3 px-6 text-center">Duration</th>
                        <th class="py-3 px-6 text-center">Total Income</th>
                        <th class="py-3 px-6 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-600 text-sm font-light">
                      <tr v-for="approvalItem in awaitingApprovalItems" :key="approvalItem.id"
                        class="border-b border-gray-200 hover:bg-gray-100">
                        <td class="py-3 px-6 text-left">
                          ({{ approvalItem.quantity }}) x {{ approvalItem.item.name || 'N/A' }}<br />
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ approvalItem.booked_dates?.start_date || 'N/A' }} -
                          {{ approvalItem.booked_dates?.end_date || 'N/A' }}<br />
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ approvalItem.quantity ? `$${approvalItem.quantity * approvalItem.item.hourly_rate}` : '$0'
                          }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          <button @click="openApprovalModal(approvalItem)"
                            class="py-1 px-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition duration-300">
                            Approve
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>

                  <RentalApproval v-if="isApprovalModalOpen" :isVisible="isApprovalModalOpen" :rental="selectedRental"
                    @close="isApprovalModalOpen = false" @approve="approveRentalApproval" />


                  <!-- Returned Table -->
                  <h3 class="text-xl font-semibold mt-6 mb-2">Returned</h3>
                  <table class="w-full border-collapse bg-[#1c1c1c] shadow-md rounded-lg overflow-hidden text-white">
                    <thead>
                      <tr class="bg-gray-700 text-gray-300 uppercase text-sm leading-normal">
                        <th class="py-3 px-6 text-left">Equipment</th>
                        <th class="py-3 px-6 text-center">Duration</th>
                        <th class="py-3 px-6 text-center">Total Income</th>
                        <th class="py-3 px-6 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-300 text-sm font-light">
                      <tr v-for="rental in returnedItems" :key="rental.id"
                        class="border-b border-gray-500 hover:bg-gray-800">
                        <td class="py-3 px-6 text-left">
                          ({{ rental.quantity }}) x {{ rental.item.name || 'N/A' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.quantity ? `$${rental.quantity * rental.item.hourly_rate}` : '$0' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.status }}
                        </td>
                      </tr>
                    </tbody>
                  </table>


                  

                  <!-- Awaiting Pickup Table -->
                  <h3 class="text-xl font-semibold mt-6 mb-2">Awaiting Pickup</h3>
                  <table class="w-full border-collapse bg-white shadow-md rounded-lg overflow-hidden">
                    <thead>
                      <tr class="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                        <th class="py-3 px-6 text-left">Equipment</th>
                        <th class="py-3 px-6 text-center">Duration</th>
                        <th class="py-3 px-6 text-center">Total Income</th>
                        <th class="py-3 px-6 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody class="text-[#1c1c1c] text-sm font-light">
                      <tr v-for="rental in awaitingPickups" :key="rental.id"
                        class="border-b border-gray-200 hover:bg-gray-100">
                        <td class="py-3 px-6 text-left">
                          ({{ rental.quantity }}) x {{ rental.item.name || 'N/A' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          {{ rental.quantity ? `$${rental.quantity * rental.item.hourly_rate}` : '$0' }}
                        </td>
                        <td class="py-3 px-6 text-center">
                          <button @click="openPickupConfirmationModal(rental.id)"
                            class="bg-blue-500 text-white px-3 py-1 rounded">
                            Confirm Pickup
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>

                </div>

                <PickupConfirmationModal :showPickupModal="showPickupConfirmationModal" :orderItem="selectedOrderItem"
                  @close="showPickupConfirmationModal = false" @confirm="handlePickupConfirmation" />



              </div>
            </div>

            <div v-else>
              <div class="empty-list-container text-center py-16">
                <i class="pi pi-exclamation-circle text-9xl text-gray-500"></i>
                <p class="text-xl text-gray-500 mt-4 mb-4">
                  Oops! You have not listed any Equipment!
                </p>

                <!-- Lease Out Button for Non-Authenticated Users -->
                <RouterLink :to="{ name: 'list-item' }">
                  <a
                    class="lease-out-button px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-lg shadow-lg transform transition duration-300 hover:scale-105 hover:shadow-2xl">
                    Add Item
                  </a>
                </RouterLink>
              </div>
            </div>
          </div>

          <!-- Edit Equipment Modal -->
          <div v-if="editModalVisible" @click.self="closeEditModal"
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 w-1/2">
              <h3 class="text-xl font-semibold mb-4">Edit Equipment</h3>
              <form @submit.prevent="updateEquipment">
                <div class="mb-4">
                  <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                  <input v-model="editedEquipment.name" type="text" id="name" class="w-full p-2 border rounded mt-1"
                    required />
                </div>

                <div class="mb-4">
                  <label for="hourly_rate" class="block text-sm font-medium text-gray-700">Hourly Rate</label>
                  <input v-model="editedEquipment.hourly_rate" type="float" id="hourly_rate"
                    class="w-full p-2 border rounded mt-1" required />
                </div>
                <!-- Available Items -->
                <div class="mb-4 relative">
                  <label for="availableItems" class="block text-sm font-medium text-gray-700">Available Items</label>
                  <input type="number" min="1" placeholder="Available items for renting out" id="availableItems"
                    v-model.number="editedEquipment.available_quantity" class="w-full p-2 border rounded mt-1" />
                </div>

                <div class="mb-4">
                  <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                  <textarea v-model="editedEquipment.description" id="description"
                    class="w-full p-2 border rounded mt-1" rows="4"></textarea>
                </div>

                <div class="mb-4">
                  <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
                  <select v-model="editedEquipment.category" id="category" class="w-full p-2 border rounded mt-1">
                    <option v-for="category in store.categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>

                <div class="mb-4">
                  <label for="is_available" class="block text-sm font-medium text-gray-700">Availability</label>
                  <select v-model="editedEquipment.is_available" id="is_available"
                    class="w-full p-2 border rounded mt-1">
                    <option :value="true">Available</option>
                    <option :value="false">Unavailable</option>
                  </select>
                </div>

                <div class="mb-4">
                  <label for="images" class="block text-sm font-medium text-gray-700">Upload Images</label>
                  <input type="file" id="images" @change="handleImageUpload" class="w-full p-2 border rounded mt-1"
                    multiple />
                </div>

                <div class="flex justify-end space-x-2">
                  <button type="button" @click="closeEditModal" class="px-4 py-2 bg-gray-400 text-white rounded">
                    Cancel
                  </button>
                  <button type="submit" class="px-4 py-2 bg-[#1c1c1c] text-[#ffc107] rounded">
                    Update
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div v-if="
            authStore.activeSection === 'my-orders' && authStore.user?.role === 'lessee'
          " id="my-orders">
            <button @click="closeSidebar"
              class="flex items-center text-gray-800 rounded-full p-2 transition hover:bg-gray-200">
              <i class="pi pi-arrreturnow-circle-left text-xl mr-2"></i> Back
            </button>

            <div class="p-6 bg-gray-100 min-h-screen">
              <h1 class="text-3xl font-bold text-gray-800 mb-4">
                Order Management
              </h1>

              <!-- Filters Section -->
              <div class="flex flex-wrap gap-4 mb-6">
                <select v-model="selectedStatus" @change="filterOrders"
                  class="px-4 py-2 bg-white border rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-300">
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rented">Rented</option>
                  <option value="pickup">Pickup Initiated</option>
                  <option value="return">Return Initiated</option>

                  <option value="rejected">Rejected</option>
                  <option value="canceled">Canceled</option>
                  <option value="completed">Completed</option>
                </select>
                <input v-model="searchQuery" @input="filterOrders" type="text" placeholder="Search by Order ID"
                  class="px-4 py-2 bg-white border rounded-md shadow-sm focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
              </div>

              <!-- Orders Table -->
              <!-- Orders Table -->
              <div class="overflow-x-auto">
                <table class="table-auto w-full border-collapse">
                  <thead>
                    <tr class="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                      <th class="py-3 px-6 text-left">Order ID</th>
                      <th class="py-3 px-6 text-center">Status</th>
                      <th class="py-3 px-6 text-center">Order Items</th>
                      <th class="py-3 px-6 text-center">Total Items</th>
                      <th class="py-3 px-6 text-center">Total Price</th>
                      <th class="py-3 px-6 text-center">Actions</th>
                    </tr>
                  </thead>

                  <tbody class="text-gray-600 text-sm font-light">
                    <tr v-for="order in filteredOrders" :key="order.id"
                      class="border-b border-gray-200 hover:bg-gray-100">
                      <td class="py-3 px-6 text-left">{{ order.id }}</td>
                      <td class="py-3 px-6 text-center">
                        <span :class="{
                          'px-3 py-1 rounded-full text-[#1c1c1c]': true,
                          'bg-yellow-500': order.status === 'pending',
                          'bg-green-300': order.status === 'pickup',
                          'bg-blue-500 text-white': order.status === 'approved',
                          'bg-orange-500': order.status === 'return',
                          'bg-green-500': order.status === 'rented',
                          'bg-red-500': order.status === 'rejected',
                          'bg-gray-500': order.status === 'completed',
                        }">
                          {{ order.status }}
                        </span>
                      </td>

                      <!-- Order Items List -->
                      <td class="py-3 px-6 text-center">
                        <div v-for="item in order.order_items" :key="item.id"
                          class="flex justify-between items-center border-b pb-2">
                          <div class="flex items-center">
                            <img v-if="item.item.images" :src="item.item.images[0]" alt="Item Image"
                              class="w-12 h-12 rounded-full object-cover mr-2" />
                            <span v-else class="text-gray-500">No image</span>
                            <p>{{ item.quantity }}x {{ item.item.name }}</p>
                          </div>

                          <!-- Confirm Button -->
                          <button v-if="item.status === 'approved'" @click="openPickupModal(item.id)"
                            class="ml-4 px-3 py-1 bg-green-500 text-white rounded shadow-sm hover:bg-green-600">
                            PickUp
                          </button>
                        </div>
                      </td>

                      <td class="py-3 px-6 text-center">{{ order.total_order_items }}</td>
                      <td class="py-3 px-6 text-center">${{ order.order_total_price }}</td>
                      <td class="py-3 px-6 text-center">
                        <button @click="openModal(order)"
                          class="px-4 py-2 bg-blue-500 text-white rounded-md shadow-sm hover:bg-blue-600">
                          Manage
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>


            </div>

            <!-- Modal -->
            <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
              <div class="bg-white rounded-lg shadow-lg w-96 p-6">
                <h2 class="text-xl font-semibold mb-4">
                  Manage Order #{{ selectedOrder.id }}
                </h2>
                <p class="mb-4">
                  Current Status: <strong>{{ selectedOrder.status }}</strong>
                </p>

                <div>
                  <button v-if="selectedOrder.status === 'pending'" @click="confirmTerminate(selectedOrder)"
                    class="px-4 py-2 bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
                    Terminate Rental
                  </button>

                  <button v-if="
                    ['rejected', 'canceled', 'completed'].includes(
                      selectedOrder.status
                    )
                  " @click="performAction(selectedOrder.id, 'reorder')"
                    class="px-4 py-2 bg-green-500 text-white rounded-md shadow-sm hover:bg-green-600">
                    Reorder
                  </button>

                  <button @click="confirmDelete(selectedOrder)"
                    class="mx-4 px-4 py-2chat bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
                    Delete Rental
                  </button>
                </div>

                <button @click="closeModal"
                  class="mt-4 px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm hover:bg-gray-400">
                  Close
                </button>
              </div>
            </div>

            <!-- Terminate Confirmation -->
            <div v-if="showTerminateConfirm"
              class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
              <div class="bg-white rounded-lg shadow-lg w-96 p-6">
                <h2 class="text-xl font-semibold mb-4">Terminate Order</h2>
                <p class="mb-4">
                  Are you sure you want to terminate Order #{{ orderToTerminate.id }}?
                </p>
                <div class="flex justify-end">
                  <button @click="performAction(orderToTerminate.id, 'terminate')"
                    class="px-4 py-2 bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
                    Yes, Terminate
                  </button>
                  <button @click="cancelTerminate"
                    class="ml-4 px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm hover:bg-gray-400">
                    Cancel
                  </button>
                </div>
              </div>
            </div>


            <!-- Delete Confirmation -->
            <div v-if="showDeleteConfirm"
              class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
              <div class="bg-white rounded-lg shadow-lg w-96 p-6">
                <h2 class="text-xl font-semibold mb-4">Delete Order</h2>
                <p class="mb-4">
                  Are you sure you want to delete Order #{{ orderToDelete.id }}?
                </p>
                <div class="flex justify-end">
                  <button @click="performAction(orderToDelete.id, 'delete')"
                    class="px-4 py-2 bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
                    Yes, Delete
                  </button>
                  <button @click="cancelDelete"
                    class="ml-4 px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm hover:bg-gray-400">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Child Modal Component -->
          <PickupModal v-if="showPickupModal" :orderItem="selectedOrderItem" @close="closePickupModal" />

          <!-- <div v-if="activeSection === 'settings'">
            <h1>My Items updated</h1>

          </div> -->

          <div v-if="authStore.activeSection === 'chats'" class="lg:px-4 py-2 min-h-screen flex flex-col lg:flex-row">
            <!-- Chat List -->
            <div v-if="!activeChat" class="w-full lg:w-3/3 bg-white shadow-lg rounded-lg overflow-hidden mb-4 lg:mb-0">
              <div class="border-b px-4 py-4 bg-[#ffc107] text-gray-800 font-bold text-lg flex items-center">
                <button @click="closeSidebar"
                  class="mr-4 text-gray-800 mt-2 rounded-full p-2 focus:outline-none transition">
                  <i class="pi pi-arrow-circle-left" style="font-size: 1.5rem"></i>
                </button>
                <div class="text-xl mr-2">💬</div>
                Chats
              </div>
              <div id="chat-container"></div>

              <ul class="divide-y divide-gray-200">
                <li v-for="chat in chats" :key="chat.id" @click="openChat(chat.id)"
                  class="px-4 py-3 hover:bg-[#ffe58a] cursor-pointer flex items-center transition">
                  <div
                    class="flex-shrink-0 w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-lg font-bold text-[#ffc107] shadow-md">
                    {{ chat.name.charAt(0) }}
                  </div>
                  <div class="ml-3 flex-1">
                    <p class="font-medium text-gray-800">{{ chat.name }}</p>
                    <p class="text-sm text-gray-600 truncate">
                      {{ chat.lastMessage }}
                    </p>
                  </div>
                  <h6 class="text-xs text-gray-500">
                    {{ formatDate(chat.created_at) }}
                  </h6>
                </li>
              </ul>
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


            <!-- Messages Window -->
            <div v-if="activeChat" class="w-full lg:h-2/3 lg:w-3/3 bg-white shadow-lg rounded-lg flex flex-col">
              <!-- Header -->
              <div class="border-b px-4 py-3 bg-[#ffc107] text-gray-800 font-bold flex items-center">
                <button @click="activeChat = null"
                  class="mr-4 text-gray-800 bg-[#ffe58a] hover:bg-[#ffd740] rounded-full p-2 focus:outline-none transition">
                  ←
                </button>
                <span>
                  {{chats.find((chat) => chat.id === activeChat)?.name}}
                </span>
              </div>



              <!-- Chat Content -->
              <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 h-60 md:h-80 lg:h-auto">
                <div v-for="message in messages[activeChat]" :key="message.id"
                  :class="message.sentBy === 'me' ? 'justify-end' : 'justify-start'" class="flex">

                  <div class="flex flex-col">
                    <!-- Image -->
                    <img v-if="message.image_url" :src="message.image_url" alt="Image"
                      class="mt-2 max-w-xs rounded-md shadow-md" />

                    <!-- Message -->
                    <p :class="{
                      'bg-[#ffe58a] text-gray-800': message.sentBy === 'me',
                      'bg-gray-200 text-gray-700': message.sentBy !== 'me',
                    }" class="inline-block px-4 py-2 rounded-sm shadow-md max-w-xs">
                      {{ message.text }}
                    </p>


                    <!-- Timestamp -->
                    <h6 class="text-xs text-gray-500 text-right mt-1">
                      {{ formatDate(message.sent_at) }}
                    </h6>
                  </div>
                </div>
              </div>

              <!-- Message Input -->
              <div class="border-t px-4 py-3 bg-gray-100 flex items-center">
                <input v-model="newMessage" type="text" placeholder="Type a message..."
                  class="flex-1 px-3 py-2 rounded-full border border-gray-300 bg-white text-gray-800 placeholder-gray-500 focus:ring-2 focus:ring-[#ffc107] outline-none shadow-sm transition" />
                <button @click="sendMessage"
                  class="ml-3 bg-[#ffc107] hover:bg-[#ffd740] text-gray-800 px-4 py-2 rounded-full shadow-md transition">
                  Send
                </button>
              </div>
            </div>

          </div>

          <div v-if="authStore.activeSection === 'reports'" class="p-6 bg-gray-50 min-h-screen">
            <!-- Back Button -->
            <button @click="closeSidebar"
              class="flex items-center text-gray-800 bg-white shadow-md rounded-full px-4 py-2 transition duration-300 transform hover:bg-gray-100 hover:shadow-lg hover:-translate-x-1">
              <i class="pi pi-arrow-circle-left text-2xl text-[#1c1c1c] mr-2"></i>
              Back
            </button>

            <div class="mt-6">
              <!-- Loading/Error States -->
              <div v-if="loading" class="flex items-center justify-center text-gray-500 space-x-2 animate-pulse">
                <i class="pi pi-spin pi-spinner text-2xl"></i>
                <span>Loading...</span>
              </div>

              <div v-else-if="error"
                class="flex items-center justify-center text-red-500 space-x-2 bg-red-100 rounded-md p-4">
                <i class="pi pi-exclamation-circle text-2xl"></i>
                <span>{{ error }}</span>
              </div>

              <!-- Report Data -->
              <div v-else>
                <!-- Lessor Report -->
                <div v-if="authStore.user?.role === 'lessor'"
                  class="bg-gradient-to-br bg-[#ffc107] rounded-lg shadow-md p-6 border-l-4 border-[#1c1c1c]">
                  <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center space-x-3">
                    <i class="pi pi-chart-bar text-yellow-500 text-3xl"></i>
                    <span>Report</span>
                  </h2>
                  <ul class="space-y-4">
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-cog text-[#1c1c1c] text-2xl"></i>
                      <span>Total Equipments</span>
                      <span class="font-bold">{{
                        report.total_equipments
                        }}</span>
                    </li>
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-shopping-cart text-[#1c1c1c] text-2xl"></i>
                      <span>Total Orders</span>
                      <span class="font-bold">{{ report.total_orders }}</span>
                    </li>
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-dollar text-yellow-500 text-2xl"></i>
                      <span>Total Revenue</span>
                      <span class="font-bold text-[#1c1c1c]">${{ report.total_revenue }}</span>
                    </li>
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-star text-[#1c1c1c] text-2xl"></i>
                      <span>Average Rating</span>
                      <span class="font-bold">{{ report.average_rating }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Lessee Report -->
                <div v-else-if="authStore.user?.role === 'lessee'"
                  class="bg-gradient-to-br bg-[#ffc107] rounded-lg shadow-md p-6 border-l-4 border-[#1c1c1c]">
                  <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center space-x-3">
                    <i class="pi pi-chart-bar text-[#1c1c1c] text-3xl"></i>
                    <span>Report</span>
                  </h2>
                  <ul class="space-y-4">
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-shopping-cart text-[#1c1c1c] text-2xl"></i>
                      <span>Total Orders</span>
                      <span class="font-bold">{{ report.total_orders }}</span>
                    </li>
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-box text-[#1c1c1c] text-2xl"></i>
                      <span>Total Rented Items</span>
                      <span class="font-bold">{{
                        report.total_rented_items
                        }}</span>
                    </li>
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-dollar text-[#1c1c1c] text-2xl"></i>
                      <span>Total Spending</span>
                      <span class="font-bold text-yellow-500">${{ report.total_spending }}</span>
                    </li>
                    <li
                      class="flex items-center justify-between bg-white p-4 rounded-md shadow-sm transition duration-300 transform hover:scale-105">
                      <i class="pi pi-star text-[#1c1c1c] text-2xl"></i>
                      <span>Average Rating Given</span>
                      <span class="font-bold">{{
                        report.average_rating_given
                        }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Unauthorized Access -->
                <div v-else
                  class="bg-red-100 text-red-600 rounded-lg shadow-lg p-6 flex items-center space-x-4 transition duration-300">
                  <i class="pi pi-lock text-3xl"></i>
                  <span class="text-lg font-semibold">Unauthorized access or role not recognized.</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Other Sections Content -->
          <div v-else>
            <p class="text-gray-600">{{ section.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal for Editing Address -->
  <div v-if="addressModalVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full sm:w-96">
      <h2 class="text-xl font-semibold mb-4">
        {{ authStore.user?.user_address.id ? "Update Address" : "Add Address" }}
      </h2>
      <div class="mb-4">
        <label for="full_name" class="block text-sm font-medium">Full Name</label>
        <input v-model="user.user_address.full_name" id="full_name" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter full name" />
      </div>
      <div class="mb-4">
        <label for="street_address" class="block text-sm font-medium">Street Address</label>
        <input v-model="user.user_address.street_address" id="street_address" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter street address" />
      </div>
      <div class="mb-4">
        <label for="street_address2" class="block text-sm font-medium">Street Address Line 2</label>
        <input v-model="user.user_address.street_address2" id="street_address2" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter street address line 2" />
      </div>
      <div class="mb-4">
        <label for="city" class="block text-sm font-medium">City</label>
        <input v-model="user.user_address.city" id="city" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter city" />
      </div>
      <div class="mb-4">
        <label for="state" class="block text-sm font-medium">State</label>
        <input v-model="user.user_address.state" id="state" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter state" />
      </div>
      <div class="mb-4">
        <label for="zip_code" class="block text-sm font-medium">Zip Code</label>
        <input v-model="user.user_address.zip_code" id="zip_code" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter zip code" />
      </div>
      <div class="mb-4">
        <label for="country" class="block text-sm font-medium">Country</label>
        <input v-model="user.user_address.country" id="country" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter country" />
      </div>
      <div class="flex justify-between">
        <button @click="addressModalVisible = false" class="px-4 py-2 bg-gray-300 text-white rounded-md">
          Cancel
        </button>
        <button @click="updateAddress" class="px-4 py-2 bg-[#1c1c1c] text-[#ffc107] rounded-md">
          <i class="bi bi-pencil-square"></i>
          {{ authStore.user?.user_address.id ? "Save Address" : "Add Address" }}
        </button>
      </div>
    </div>
  </div>

  <!-- Modal for Editing Phone Number -->
  <div v-if="phoneModalVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full sm:w-96">
      <h2 class="text-xl font-semibold mb-4">Update Phone Number</h2>
      <div class="mb-4">
        <input v-model="phoneNumber" id="phone_number" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full"
          :placeholder="authStore.user?.phone_number || 'Enter phone number'" />
      </div>
      <div class="flex justify-between">
        <button @click="phoneModalVisible = false" class="px-4 py-2 bg-gray-300 text-white rounded-md">
          Cancel
        </button>
        <button @click="updatePhoneNumber" class="px-4 py-2 bg-[#1c1c1c] text-[#ffc107] rounded-md">
          Update
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, defineProps, defineEmits } from 'vue';
import axios from "axios";
import { useAuthStore } from "@/store/auth";
import useNotifications from "@/store/notification.js"; // Import the notification service
import { useEquipmentsStore } from "@/store/equipments";
import { useChatStore } from "@/store/chat";
import { useRouter, useRoute } from "vue-router";
import { format } from "date-fns";
import Cookies from "js-cookie";
import PickupModal from './PickupModal.vue'; // Import the child modal component
import PickupConfirmationModal from './PickupConfirmationModal.vue';
import RentalApproval from './RentalApproval.vue';
import ReturnConfirmationModal from "./ReturnConfirmationModal.vue"; // Adjust path if needed
import { result } from 'lodash';

const isApprovalModalOpen = ref(false);

// Open modal with selected approval rental details
const openApprovalModal = (approvalItem) => {
  selectedRental.value = approvalItem;
  isApprovalModalOpen.value = true;
};

// Approve rental and send API request
const approveRentalApproval = async (approvalItem) => {
  if (!approvalItem?.id) return;

  try {
    const response = await axios.post(
      `${api_base_url}/api/order-items/${approvalItem.id}/approve/`,
      {},
      { withCredentials: true }
    );

    approvalItem.status = 'approved';

    showNotification("Success", " Rental Approved Successfully!", "success"); // Notify user
    router.push('/');



    isApprovalModalOpen.value = false;
  } catch (error) {
    showNotification("Error", " Rental Approval Failed!", "error"); // Notify user
  }
};

// Reactive stateconst showPickupModal = ref(false);
const selectedRental = ref(null);
const showPickupConfirmationModal = ref(null);

const openPickupConfirmationModal = (rental) => {
  selectedOrderItem.value = rental;
  showPickupConfirmationModal.value = true;
};

const closePickupConfirmationModal = () => {
  showPickupConfirmationModal.value = false;
  selectedOrderItem.value = null;
};

const handlePickupConfirmation = () => {
  closePickupModal();
};


const showPickupModal = ref(false);

const { showNotification } = useNotifications(); // Initialize notification service


// Open the modal

const openPickupModal = (order) => {

  selectedOrderItem.value = order; // Example order data

  showPickupModal.value = true;

};


// Close the modal

const closePickupModal = () => {

  showPickupModal.value = false;

};

const chats = ref([]); // List of chats
const messages = reactive({}); // Messages for each chat, keyed by chat ID
const activeChat = ref(null); // Currently open chat ID
const newMessage = ref(""); // Message being typed
const showTerminateConfirm = ref(false);





const showReturnModal = ref(false);

// Function to open the modal and set the selected order item
const openReturnModal = (orderItemId) => {
  selectedOrderItem.value = orderItemId;
  showReturnModal.value = true;
};

// Function to close the modal
const closeReturnModal = () => {
  showReturnModal.value = false;
};

// Function to handle return confirmation
const handleReturnConfirmation = (returnData) => {

  axios.post(`${api_base_url}/api/order-items/${selectedOrderItem.value}/confirm_return/`, returnData, {
    withCredentials: true, // Ensure credentials (cookies/session) are sent
  })
    .then(response => {
      showNotification("Success", "Item Return confirmed successfully!", "success"); // Notify user
      router.push('/');
    })
    .catch(error => {

      // Extract detailed error message if available
      let errorMessage = "Error confirming return. Please try again.";
      if (error.response) {
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data && typeof error.response.data === "string") {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      showNotification(errorMessage, "error"); // Notify user with specific error
    });

  showReturnModal.value = false;
};



const store = useEquipmentsStore();
const chatStore = useChatStore();
const authStore = useAuthStore();

const categories = ref([]);

const api_base_url = import.meta.env.VITE_API_BASE_URL;


// Check if equipment is editable
const isEditable = (id) => store.userEditableEquipmentsIds.includes(id);

const report = ref({});
const error = ref(null);

const fetchUserReport = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/reports/`, {
      withCredentials: true, // Include credentials (cookies) in the request
    });

    report.value = response.data;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};


// Handle Logout functionality
const handleLogout = async () => {
  await authStore.logout(); // Wait for the logout method to finish
  router.push("/"); // Redirect to login page
};

const editModalVisible = ref(false);
const editedEquipment = reactive({
  id: null,
  name: "",
  hourly_rate: "",
  description: "",
  category: null,
  is_available: true,
  images: null,
});

const openEditModal = async (equipment) => {
  Object.assign(editedEquipment, equipment); // Clone the equipment into the editedEquipment
  await store.fetchCategories(); // Fetch categories for the dropdown
  editModalVisible.value = true;
};

const closeEditModal = () => {
  editModalVisible.value = false;
  Object.assign(editedEquipment, {
    id: null,
    name: "",
    hourly_rate: "",
    description: "",
    category: null,
    is_available: true,
    image: null,
  });
};

const handleImageUpload = (event) => {
  const files = event.target.files;
  if (files.length > 0) {
    // Store the selected files in an array
    editedEquipment.images = Array.from(files); // Store multiple images in an array
  }
};

const updateEquipment = async () => {
  const formData = new FormData();

  // Append regular fields to the formData
  formData.append("name", editedEquipment.name);
  formData.append("hourly_rate", editedEquipment.hourly_rate);
  formData.append("available_quantity", editedEquipment.available_quantity);
  formData.append("description", editedEquipment.description);
  formData.append("category", editedEquipment.category);
  formData.append("is_available", editedEquipment.is_available);

  // Append images only if they are provided
  if (editedEquipment.images && editedEquipment.images.length > 0) {
    for (const image of editedEquipment.images) {
      formData.append("images", image); // Append each image as 'images[]'
    }
  }

  try {
    // Make the API call to update the equipment
    await axios.put(
      `${api_base_url}/api/equipments/${editedEquipment.id}/`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    showNotification("Success", "Item updated successfully!", "success"); // Notify user

    // Close the modal and refresh the equipment list after successful update
    closeEditModal();
    await store.fetchUserEquipments(); // Refresh the equipment list
  } catch (error) {
  }
};

// Fetch the list of chats
const fetchChats = async () => {
  try {
    const response = await axios.get(
      `${api_base_url}/api/accounts/chats/`,
      { withCredentials: true }
    );

    chats.value = response.data.map((chat) => {
      const otherParticipant = chat.participants.find(
        (participant) => participant.id !== authStore.user?.id
      );

      return {
        id: chat.id,
        name: otherParticipant?.username || "Unknown",
        lastMessage: chat.messages.length
          ? chat.messages[chat.messages.length - 1].content
          : "No messages yet",
        created_at: chat.created_at,
        participants: chat.participants,
      };
    });
  } catch (error) {
  }
};

// Fetch messages for a specific chat
const fetchMessages = async (chatId) => {
  try {
    const response = await axios.get(
      `${api_base_url}/api/accounts/chats/${chatId}/`,
      {
        withCredentials: true,
      }
    );

    messages[chatId] = response.data.messages.map((msg) => ({
      id: msg.id,
      text: msg.content,
      sentBy: msg.sender === authStore.user?.id ? "me" : "them",
      sent_at: msg.sent_at,
      sender: msg.sender,
      image_url: msg.image_url,
    }));
    activeChat.value = chatId;

  } catch (error) {
  }
};

// Send a new message
const sendMessage = async () => {
  if (!newMessage.value.trim()) return; // Don't send empty messages

  try {
    const response = await axios.post(
      `${api_base_url}/api/accounts/messages/`,
      {
        content: newMessage.value,
        chat: activeChat.value, // Current chat ID
        receiver: getReceiverId(activeChat.value), // Get receiver ID for this chat
      },
      { withCredentials: true }
    );

    fetchMessages(activeChat.value);
    newMessage.value = ""; // Clear input field
  } catch (error) {
  }
};

// Open a chat and fetch its messages
const openChat = (chatId) => {
  if (!messages[chatId]) {
    fetchMessages(chatId);
  } else {
    activeChat.value = chatId;
  }
};

// Get the receiver's ID for a given chat
const getReceiverId = (chatId) => {
  const chat = chats.value.find((c) => c.id === chatId);
  const receiver =
    chat.participants[0] !== authStore.user?.id
      ? chat.participants[0].id
      : chat.participants[1].id;

  return receiver;
};

// Initialize the auth store
const router = useRouter();
const showModal = ref(false);
const selectedOrder = ref(null);
const selectedOrderItem = ref(null);

const showDeleteConfirm = ref(false);
const orderToDelete = ref(null);
const orderToTerminate = ref(null);

const openModal = (order) => {
  selectedOrder.value = order;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedOrder.value = null;
  showDeleteConfirm.value = false;
  showTerminateConfirm.value = false;
};



const confirmDelete = (order) => {
  orderToDelete.value = order;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  showDeleteConfirm.value = false;
  orderToDelete.value = null;
};

const deleteOrder = (orderId) => {
  // API call to delete the order
  showDeleteConfirm.value = false;
  closeModal();
  // Remove order from UI after success
};

// Trigger the termination confirmation modal
const confirmTerminate = (order) => {
  orderToTerminate.value = order;
  showTerminateConfirm.value = true;
};

// Close the termination confirmation modal
const cancelTerminate = () => {
  showTerminateConfirm.value = false;
  orderToTerminate.value = null;

};

// Handle order action
const performAction = async (order, action) => {
  try {
    const response = await axios.post(
      `${api_base_url}/api/orders/${order}/${action}/`,
      {},
      {
        withCredentials: true, // This ensures cookies (credentials) are sent with the request
      }
    );
    showModal.value = false;
    await fetchOrders(); // Refresh order list
    closeModal();
  } catch (error) {
    alert(error.response?.data?.error || "An error occurred");
  }
};

// Computed property for active section based on user role

const roleSection = computed(() => {
  return authStore.user?.role === 'lessee' ? 'my-orders' : 'my-equipments';
});
const phoneNumber = ref("");

// Fetch user equipments on mount with credentials
const fetchUserEquipments = async () => {
  store.fetchUserEditableEquipments;
};

const awaitingApprovalItems = computed(() => {
  const result = Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'pending')
    : [];
  return result;
});

const rentedItems = computed(() => {
  const result = Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'rented')
    : [];
  return result;
});

const returnedItems = computed(() => {
  const result = Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'completed')
    : [];
  return result;
});

const awaitingPickups = computed(() => {
  const result = Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'pickup')
    : [];
  return result;
});

const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: "equipment-details", params: { id: equipmentId } });
  } else {
  }
};

const orders = ref([]);
const orderItems = ref([]);
const filteredOrders = ref([]);
const searchQuery = ref("");
const selectedStatus = ref("");
const loading = ref(true);

const fetchOrders = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/orders/`, {
      withCredentials: true,
    });
    orders.value = response.data;
    filteredOrders.value = response.data; // Initial population
  } catch (error) {
  } finally {
    loading.value = false;
  }
};


const fetchOrderItems = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/order-items/`, {
      withCredentials: true,
    });
    orderItems.value = response.data;
  } catch (error) {
  } finally {
    loading.value = false;
  }
};

const filterOrders = () => {
  filteredOrders.value = orders.value.filter((order) => {
    return (
      (selectedStatus.value
        ? order.status === selectedStatus.value
        : true) &&
      (searchQuery.value
        ? order.id.toLowerCase().includes(searchQuery.value.toLowerCase())
        : true)
    );
  });
};

// Mock user object for demonstration purposes
const user = ref({
  user_address: {
    full_name: "", // Default value
    street_address: "",
    city: "",
    state: "",
    zip_code: "",
    country: "",
  },
});
const addressModalVisible = ref(false);
const phoneModalVisible = ref(false);
const showSidebar = ref(true); // Sidebar visibility state

const closeSidebar = () => {
  showSidebar.value = true;
  authStore.activeSection = null;
};

// Method to set the active section
const setActiveSection = (sectionName) => {
  authStore.activeSection = sectionName;
};


const route = useRoute();



// Function to navigate to a section
const navigateToSection = (sectionName) => {
  authStore.activeSection = sectionName;

  // Scroll to the section
  const sectionElement = document.getElementById(sectionName);
  if (sectionElement) {
    sectionElement.scrollIntoView({ behavior: "smooth" });
  }

  // Hide sidebar on small devices
  if (window.innerWidth < 1024) {
    showSidebar.value = false;
  }

};


const sections = computed(() => [
  { name: "personal-info", label: "Personal Information" },
  {
    name: "my-equipments",
    label: "My Items",
    show: authStore.user?.role === "lessor",
  },
  {
    name: "my-orders",
    label: "My Orders",
    show: authStore.user?.role === "lessee",
  },
  { name: "chats", label: "Chats" },
  { name: "reports", label: "Reports" },
]);
const otherSections = [
  {
    name: "my-equipments",
    label: "My Items",
    show: authStore.user?.role === "lessor",
  },
  {
    name: "my-orders",
    label: "My Orders",
    show: authStore.user?.role === "lessee",
  },
  // { name: "settings", label: "Settings" },
  { name: "chats", label: "Chats" },
  { name: "reports", label: "Reports" },
];

// Filter sections to only include those that should be shown
const visibleSections = computed(() =>
  sections.value.filter((section) => section.show !== false)
);




const uploadProfilePicture = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await axios.put(
      `${api_base_url}/api/accounts/users/${authStore.user?.id}/`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        withCredentials: true, // Include authentication cookies
      }
    );

    user.image = response.data.image_url; // Update the image URL
    await authStore.getUserData();
  } catch (error) {
  }
};

// Update phone number via PUT request
const updatePhoneNumber = async () => {
  try {
    const updatedUserData = { phone_number: phoneNumber.value };
    const response = await axios.put(
      `${api_base_url}/api/accounts/users/${authStore.user?.id}/`,
      updatedUserData,
      { withCredentials: true }
    );
    authStore.user = response.data;

    phoneModalVisible.value = false;
  } catch (error) {
  }
};

const updateAddress = async () => {
  try {
    const updatedAddressData = {
      full_name: user.value.user_address?.full_name || "",
      street_address: user.value.user_address?.street_address || "",
      street_address2: user.value.user_address?.street_address2 || "",
      city: user.value.user_address?.city || "",
      state: user.value.user_address?.state || "",
      zip_code: user.value.user_address?.zip_code || "",
      country: user.value.user_address?.country || "",
    };

    let response;
    if (user.value.user_address.id) {
      // Update existing address
      response = await axios.put(
        `${api_base_url}/api/accounts/physical-addresses/${user.value.user_address.id}/`,
        updatedAddressData,
        { withCredentials: true }
      );
    } else {
      // Add new address
      response = await axios.post(
        `${api_base_url}/api/accounts/physical-addresses/`,
        updatedAddressData,
        { withCredentials: true }
      );
    }

    user.value.user_address = response.data;
    addressModalVisible.value = false;
  } catch (error) {
  }
};

const formatDate = (date) => {
  try {
    return format(new Date(date), "Ppp");
  } catch (error) {
    return "Invalid Date";
  }
};

// Fetch user data when the component is mounted
onMounted(async () => {
  const section = route.query.section;
  if (section) {
    navigateToSection(section);
  }
  await authStore.getUserData();
  user.value = authStore.user;

  fetchChats();
  fetchOrders(); // Fetch orders on mount
  fetchOrderItems();
  fetchUserReport();
  await store.fetchUserEditableEquipments();
});


</script>
