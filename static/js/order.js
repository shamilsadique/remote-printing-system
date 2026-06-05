document.addEventListener("DOMContentLoaded", function () {
    // Get form elements
    const fileInput = document.getElementById("file");
    const printType = document.getElementById("print-type");
    const paperSize = document.getElementById("paper-size");
    const copies = document.getElementById("copies");
    const priceDisplay = document.getElementById("price-display");

    // Price configuration 
    const basePrice = {
        "black-white": 1.5,
        "color": 5.0
    };

    const paperMultiplier = {
        "A4": 1.0,
        "A3": 1.5,
        "Letter": 1.2,
        "Legal": 1.3
    };

    // Function to calculate price
    function calculatePrice() {
        let printCost = basePrice[printType.value] || 0.10;
        let paperCost = paperMultiplier[paperSize.value] || 1.0;
        let copyCount = parseInt(copies.value) || 1;
        let fileSize = fileInput.files[0] ? fileInput.files[0].size / 1024 / 1024 : 0; // Convert to MB
        
        let fileCost = fileSize * 1.0; 
        
        let totalPrice = ((printCost * paperCost) + fileCost) * copyCount;
        totalPrice = totalPrice.toFixed(2); 
        
        priceDisplay.innerHTML = `<strong>Total Price: ₹${totalPrice}</strong>`;
    }

    // Event listeners
    fileInput.addEventListener("change", calculatePrice);
    printType.addEventListener("change", calculatePrice);
    paperSize.addEventListener("change", calculatePrice);
    copies.addEventListener("input", calculatePrice);
});
