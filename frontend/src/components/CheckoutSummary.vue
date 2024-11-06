<template>
<div class="container mx-auto py-8">
    <!-- Cart Table -->
    <div class="overflow-x-auto mb-8">
        <table class="min-w-full bg-white border border-gray-300 rounded-lg shadow-md">
            <thead>
                <tr class="bg-gray-100 text-gray-600 uppercase text-sm leading-normal">
                    <th class="py-3 px-6 text-left">Product</th>
                    <th class="py-3 px-6 text-right">Total</th>
                </tr>
            </thead>
            <tbody class="text-gray-600 text-sm font-light">
                <tr class="border-b border-gray-200 hover:bg-gray-100">
                    <td class="py-3 px-6">Handbag fringilla <strong> × 2</strong></td>
                    <td class="py-3 px-6 text-right">$165.00</td>
                </tr>
                <tr class="border-b border-gray-200 hover:bg-gray-100">
                    <td class="py-3 px-6">Handbag justo <strong> × 2</strong></td>
                    <td class="py-3 px-6 text-right">$50.00</td>
                </tr>
                <tr class="border-b border-gray-200 hover:bg-gray-100">
                    <td class="py-3 px-6">Handbag elit <strong> × 2</strong></td>
                    <td class="py-3 px-6 text-right">$50.00</td>
                </tr>
                <tr class="border-b border-gray-200 hover:bg-gray-100">
                    <td class="py-3 px-6">Handbag Rutrum <strong> × 1</strong></td>
                    <td class="py-3 px-6 text-right">$50.00</td>
                </tr>
            </tbody>
            <tfoot>
                <tr class="bg-gray-100 font-semibold">
                    <th class="py-3 px-6 text-left">Cart Subtotal</th>
                    <td class="py-3 px-6 text-right">$215.00</td>
                </tr>
                <tr class="bg-gray-100 font-semibold">
                    <th class="py-3 px-6 text-left">Shipping</th>
                    <td class="py-3 px-6 text-right"><strong>$5.00</strong></td>
                </tr>
                <tr class="bg-gray-100 border-t border-gray-300 font-bold">
                    <th class="py-3 px-6 text-left">Order Total</th>
                    <td class="py-3 px-6 text-right"><strong>$220.00</strong></td>
                </tr>
            </tfoot>
        </table>
    </div>

    <!-- Payment Method -->
    <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-xl font-semibold mb-4">Payment Method</h3>
        <form>
            <div class="mb-4">
                <input id="payment_default" name="check_method" type="radio" required class="hidden">
                <label for="payment_default" class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-100">
                    <img src="" alt="" class="w-6 h-6 mr-3">
                    <span class="text-gray-700">PayPal</span>
                </label>
                <div class="mt-2 px-4 py-2 bg-gray-50 rounded-lg shadow-sm">
                    <p class="text-sm text-gray-600">Pay via PayPal; you can pay with your credit card if you don’t have a PayPal account.</p>
                  </div>
            </div>

            <div class="mb-4">
                <input id="stripe_payment" name="check_method" type="radio" required class="hidden">
                <label for="stripe_payment" class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-100">
                    <img src="" alt="" class="w-6 h-6 mr-3">
                    <span class="text-gray-700">Stripe</span>
                </label>
                <div class="mt-2 px-4 py-2 bg-gray-50 rounded-lg shadow-sm">
                    <p class="text-sm text-gray-600">Pay securely using your credit card via Stripe.</p>
                </div>
            </div>

            <div class="mt-6">
                <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200">Proceed to Payment</button>
            </div>
        </form>
    </div>
</div>
</template>
   
<script>

</script>

<style scoped>
/* Additional styles can go here if needed */
</style>