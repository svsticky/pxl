//Set global used to evade unnecesary builds
var prev_column_count = -1;
//Execute on every resize
window.onresize = build; 
//Execute on startup (import as defer)
build();

function build() {
  let column_count = 5; //baseline value

  //Determine the column count by screen width
  //Note that these exact values are also hardcoded in the css
  if (window.innerWidth < 1200) column_count = 3;
  if (window.innerWidth < 800)  column_count = 1;

  //Return if no change will take place
  if (prev_column_count == column_count) return;
  prev_column_count = column_count;

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

  //Casino style hand out all the photos to the columns
  for (let i=0; i<photos.length; i++) 
  {
    columns[i%column_count].appendChild(photos[i].cloneNode(true));
  }
}

function range(start, end) {
  return Array(end - start + 1).fill().map((_, idx) => start + idx)
}
