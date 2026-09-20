// =========================
// Smooth Scroll
// =========================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        document.querySelector(this.getAttribute("href"))
            .scrollIntoView({

                behavior: "smooth"

            });

    });

});


// =========================
// Navbar Shadow
// =========================

window.addEventListener("scroll", function () {

    const nav = document.querySelector("nav");

    if (window.scrollY > 50) {

        nav.style.boxShadow = "0 8px 20px rgba(0,0,0,.15)";

    }

    else {

        nav.style.boxShadow = "none";

    }

});


// =========================
// Fade Animation
// =========================

const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {

            entry.target.classList.add("show");

        }

    });

});

document.querySelectorAll(

".service-card,.gallery-card,.review-card,.price-card"

).forEach(el => {

    el.classList.add("hidden");

    observer.observe(el);

});


// =========================
// Booking Form Validation
// =========================

const form = document.querySelector(".booking-form");

if(form){

form.addEventListener("submit", function(e){

const phone = document.querySelector(

'input[name="phone"]'

).value;

if(phone.length != 10){

alert(

"Please Enter Valid 10 Digit Mobile Number"

);

e.preventDefault();

}

});

}


// =========================
// Back To Top Button
// =========================

const topBtn = document.createElement("button");

topBtn.innerHTML = "↑";

topBtn.id = "topBtn";

document.body.appendChild(topBtn);

window.addEventListener("scroll", ()=>{

if(window.scrollY>400){

topBtn.style.display="block";

}

else{

topBtn.style.display="none";

}

});

topBtn.onclick=()=>{

window.scrollTo({

top:0,

behavior:"smooth"

});

};