let signup_btn = document.getElementById("signup_btn");
let login_section = document.getElementById("login_section");
let signup_section = document.getElementById("signup_section");
let login_content = document.getElementById("login_content");
let signup_content = document.getElementById("signup_content");
let signup_expanded = document.getElementById("signup_expanded");
let signup_back_btn = document.getElementById("signup_back_btn");

function expandSignup() {
  login_section.classList.remove("w-2/3");
  login_section.classList.add("w-0");
  login_content.classList.add("hidden");
  signup_section.classList.remove("w-1/3");
  signup_section.classList.add("w-full");
  signup_section.classList.add("rounded-l-xl");
  signup_content.classList.add("hidden");
  signup_expanded.classList.remove("hidden");
}

function collapseSignup() {
  login_section.classList.remove("w-0");
  login_section.classList.add("w-2/3");
  login_content.classList.remove("hidden");
  signup_section.classList.remove("w-full");
  signup_section.classList.add("w-1/3");
  signup_section.classList.remove("rounded-l-xl");
  signup_content.classList.remove("hidden");
  signup_expanded.classList.add("hidden");
}

signup_btn.addEventListener("click", function () {
  expandSignup();
});

signup_back_btn.addEventListener("click", function () {
  collapseSignup();
});
