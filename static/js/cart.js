// Get references to the dropdown and full price element
const deliverySelect = document.querySelector('select[name="delivery"]');
const originalFullPrice = document.getElementById("original-full-price");
const changingFullPrice = document.getElementById("full-price");

console.log(deliverySelect);
console.log(originalFullPrice);
console.log(changingFullPrice);

// Event listener for dropdown changes
deliverySelect.addEventListener("change", () => {
  const selectedDelivery = deliverySelect.value;
  const deliveryPrice = parseInt(selectedDelivery);
  const fullPriceValue = parseInt(originalFullPrice.textContent);
  const updatedFullPrice = fullPriceValue + deliveryPrice;

  changingFullPrice.textContent = `${updatedFullPrice.toFixed(2)}`; // Format to 2 decimal places
});