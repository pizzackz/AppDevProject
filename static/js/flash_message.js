if (document.querySelector(".popup:not(.alert-dismissible)")) {
  const popup = document.querySelector(".popup:not(.alert-dismissible)");
  const closeButton = document.querySelector(".popup button");
  
  closeButton.addEventListener("click", () => {
    popup.classList.add("close");
  });
  
  setTimeout(() => {
    if (popup) {
      popup.classList.add("close");
    }
  }, 10000);
}