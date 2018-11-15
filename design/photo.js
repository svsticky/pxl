// define constant keycode values for arrow keys
const LEFT_ARROW = 37;
const RIGHT_ARROW = 39; 

// bind navigation elementts
const left = document.getElementById("left");
const right = document.getElementById("right");

// KeyPress -> Maybe ClickEvent
document.onkeydown = (ev) => {
   switch(ev.keyCode)
   {
     case LEFT_ARROW: left.click(); break;
     case RIGHT_ARROW: right.click(); break;
   }
}
