// Define constant keycode values for navigation keys
const ESCAPE = 27;
const LEFT_ARROW = 37;
const RIGHT_ARROW = 39;

// Bind navigation elementts. Back is for back to album.
const back = document.getElementById("back");
const prev = document.getElementById("prev");
const next = document.getElementById("next");

// KeyPress -> Maybe ClickEvent
document.onkeyup = (ev) => {
  switch(ev.keyCode)
  {
    case LEFT_ARROW:
      if (prev != null) { prev.click(); }
      break;
    case RIGHT_ARROW:
      if (next != null) { next.click(); }
      break;
    case ESCAPE:
      if (back != null) { back.click(); }
      break;
  }
}
