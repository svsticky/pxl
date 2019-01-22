// define constant keycode values for arrow keys
const LEFT_ARROW = 37;
const RIGHT_ARROW = 39;

// bind navigation elementts
const prev = document.getElementById("prev");
const next = document.getElementById("next");

// KeyPress -> Maybe ClickEvent
document.onkeydown = (ev) => {
  switch(ev.keyCode)
  {
    case LEFT_ARROW:
      if (prev != null) { prev.click(); }
      break;
    case RIGHT_ARROW:
      if (next != null) { next.click(); }
      break;
  }
}
