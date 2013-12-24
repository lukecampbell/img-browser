
function handleKey(evt) {
  var nextpage = $("#next")
  var prevpage = $("#prev")
  nexturl = nextpage.attr("href")
  prevurl = prevpage.attr("href")
  evt = evt || window.event;
  switch (evt.keyCode) {
          case 37:
          window.location = prevurl;
          break;

          case 39:
          window.location = nexturl;
          break;
  }
};

