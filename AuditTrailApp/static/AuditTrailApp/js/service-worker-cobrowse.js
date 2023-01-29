
self.addEventListener('notificationclick', function(event) {
  var notification = event.notification;
  var redirect_url = notification.data.url;
  var action = event.action;

  if (action === 'close') {
      notification.close();
  } 
  else {
      if (redirect_url != null) {
          clients.openWindow(redirect_url);
      }
      notification.close();
  }
});