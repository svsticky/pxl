//Set global used to evade unnecesary builds
var prev_column_count = -1;
//Execute on every resize
window.onresize = build; 
//Execute on startup (import as defer)
build();

function build() {
  let column_count = 5; //baseline value

  //Determine the column count by screen width
  if (window.innerWidth < 1200) column_count = 3;
  if (window.innerWidth < 800)  column_count = 1;

  //Return if no change will take place
  if (prev_column_count == column_count) return;
  prev_column_count = column_count;

  console.log("building...");

  //First clean up all columns
  range(1,5).map(x => { 
    let el = document.getElementById("photo-column"+x)
    while (el.firstChild)
      el.removeChild(el.firstChild);
  });

  //Bind all needed resources
  let container = document.getElementById("photo-container");
  let photos = container.querySelectorAll(".photo");
  let columns = range(1,column_count).map(x => document.getElementById("photo-column"+x));

  console.log(columns)
  //Casino style hand out all the photos to the columns
  for (let i=0; i<photos.length; i++) 
  {
    columns[i%column_count].appendChild(photos[i].cloneNode(true));
  }
  return columns;
}

function range(start, end) {
  return Array(end - start + 1).fill().map((_, idx) => start + idx)
}


/* TEST FUNCTION FOR SPAWNING A 1000 PICTURES IN THE CONTAINER
function init() {
  let container = document.getElementById("photo-container");
  for(let i=0; i<1000; i++)
  {
    let el = document.createElement("div")
    el.classList.add("photo")
    let img = document.createElement("img")
    img.src = "ex" + (Math.floor(Math.random()*5)+1) + ".jpeg"
    el.appendChild(img)
    container.appendChild(el);
  }
  return container; 
}*/
