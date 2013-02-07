var req = new XMLHttpRequest();
req.open(
    "GET",
    "http://localhost:8082?" +
    document.location,
    true);
req.onload = display();
req.send(null);

function display() {
  console.log("Successfully Sent Message to Server")
}

