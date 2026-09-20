const bookingForm = document.querySelector("form");

if(bookingForm){

bookingForm.addEventListener("submit",(e)=>{

const phone=document.querySelector(
'input[name="phone"]'
).value;

if(phone.length!=10){

alert("Enter Valid Mobile Number");

e.preventDefault();

}

});

}