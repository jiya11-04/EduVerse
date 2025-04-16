// cart.js

function addToCart(itemName, price) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.push({ name: itemName, price: price });
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartIcon();
  }
  
  function updateCartIcon() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const count = cart.length;
    const cartCounter = document.getElementById('cart-counter');
    if (cartCounter) cartCounter.textContent = count;
  }
  
  function getCartItems() {
    return JSON.parse(localStorage.getItem('cart')) || [];
  }
  
  function clearCart() {
    localStorage.removeItem('cart');
    updateCartIcon();
  }
  
  window.onload = updateCartIcon;
  