let scale = 1;
const map = document.getElementById("map");

/* retrieves html document, adds a 
listender which waits for a user to click
then scales the image + or - */

document.getElementById("zoomIn").addEventListener("click", () => {
  scale += 0.2;
  map.style.transform = `scale(${scale})`;
});

document.getElementById("zoomOut").addEventListener("click", () => {
  if (scale > 0.4) {
    scale -= 0.2;
    map.style.transform = `scale(${scale})`;  //changes the scale variable for map
  }
});

