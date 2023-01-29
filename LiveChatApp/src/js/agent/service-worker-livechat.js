self.addEventListener('notificationclick', function(event) {
    let notification = event.notification;
    let redirect_url = notification.data.url;
    let action = event.action;
  
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