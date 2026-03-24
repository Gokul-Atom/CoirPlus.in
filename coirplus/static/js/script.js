const tooltipEls = document.querySelectorAll("*[data-bs-toggle='tooltip']");
tooltipEls.forEach((el) => {
  new bootstrap.Tooltip(el);
});

const scrollToTop = document.querySelector("#scroll-to-top");
if (scrollToTop) {
  window.addEventListener("scroll", () => {
    if (window.scrollY > window.innerHeight) {
      scrollToTop.classList.add("show");
    } else {
      scrollToTop.classList.remove("show");
    }
  });
  scrollToTop.addEventListener("click", () => {
    window.scrollTo(0, 0);
  });
}

document.addEventListener("alpine:init", () => {
  Alpine.store("cart", { quantity: 0 });
  Alpine.store("wishlist", { quantity: 0 });
});
