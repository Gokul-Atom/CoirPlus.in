const tooltipEls = document.querySelectorAll("*[data-bs-toggle='tooltip']");
tooltipEls.forEach((el) => {
  new bootstrap.Tooltip(el);
});

const scrollToTop = document.querySelector("#scroll-to-top");
if (scrollToTop) {
  scrollToTop.addEventListener("click", () => {
    window.scrollTo(0, 0);
  });
}
