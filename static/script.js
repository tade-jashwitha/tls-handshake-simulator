function startSimulation(){

const packet = document.getElementById("packet")
const stepsList = document.getElementById("steps")

stepsList.innerHTML=""

fetch("/simulate")
.then(response => response.json())
.then(data => {

data.forEach((step,index)=>{

setTimeout(()=>{

let li=document.createElement("li")
li.innerText=step
stepsList.appendChild(li)

/* Move packet */

if(step.includes("Client →")){
packet.style.left="270px"
}

else if(step.includes("Server →")){
packet.style.left="0px"
}

/* Secure session color */

if(step.includes("Secure")){
packet.style.background="green"
}

}, index*1500)

})

})

}