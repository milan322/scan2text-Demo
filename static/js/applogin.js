
console.log("logging test milan-login app----");
window.fbAsyncInit = function() {
    FB.init({
        appId      : '1706950096293019', // App ID
        channelUrl : 'http://localhost:9000/channel.html',
        status     : true, // check login status
        cookie     : true, // enable cookies to allow the server to access the session
        xfbml      : true  // parse XFBML
    });

    FB.Event.subscribe('auth.authResponseChange', function(response) 
    {
        if (response.status === 'connected') 
        {
            console.log("you are logged in facebook!");
            document.getElementById("message").innerHTML +=  "<br>Connected to Facebook";
        } 

    });

};
 
(function(d){
     var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement('script'); js.id = id; js.async = true;
     js.src = "//connect.facebook.net/en_US/all.js";
     ref.parentNode.insertBefore(js, ref);
}(document));

 function Logout()
{
    console.log("logging you out please wait !--")
    FB.getLoginStatus(function(response) {
        if (response && response.status === 'connected') {
            FB.logout(function(response) {
                document.location.reload();
            });
        }
    });
}

