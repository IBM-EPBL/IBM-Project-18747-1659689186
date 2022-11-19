// let noOfCharac = 150;
// let contents = document.querySelectorAll(".description");
// contents.forEach(content => {
//     //If text length is less that noOfCharac... then hide the read more button
//     if(content.textContent.length < noOfCharac){
//         content.nextElementSibling.style.display = "none";
//     }
//     else{
//         let displayText = content.textContent.slice(0,noOfCharac);
//         let moreText = content.textContent.slice(noOfCharac);
//         content.innerHTML = `${displayText}<span class="dots">...</span><span class="hide more">${moreText}</span>`;
//     }
// });

// function readMore(btn){
//     let post = btn.parentElement;
//     post.querySelector(".dots").classList.toggle("hide");
//     post.querySelector(".more").classList.toggle("hide");
//     btn.textContent == "Read More" ? btn.textContent = "Read Less" : btn.textContent = "Read More";
// }