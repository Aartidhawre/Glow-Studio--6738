const search=document.querySelector("#search");

if(search){

search.addEventListener("keyup",()=>{

let filter=search.value.toUpperCase();

let tr=document.querySelectorAll("tbody tr");

tr.forEach(row=>{

let td=row.children[1];

if(td){

let txt=td.textContent;

if(txt.toUpperCase().indexOf(filter)>-1){

row.style.display="";

}else{

row.style.display="none";

}

}

});

});

}