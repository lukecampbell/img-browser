
function handleKey(evt) {
  var url = document.URL;
  var i = url.lastIndexOf('/');
  var s = url.substring(i+1);
  i = parseInt(s);
  evt = evt || window.event;
  switch (evt.keyCode) {
          case 37:
              i--;
              window.location = '/view/' + i;
              break;

          case 39:
              i++;
              window.location = '/view/' + i;
              break;

          case 38:
              i = parseInt(i / (rows * cols));
              s = '/browse/' + i;
              window.location = s;
              break;
  }
};

