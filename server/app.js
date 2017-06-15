var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser'); // used for session cookie
var bodyParser = require('body-parser');
// simple in-memory session is used here. use connect-redis for production!!
var session = require('express-session');
var proxy = require('./routes/proxy'); // used when requesting data from real services.

var index = require('./routes/index');

// get config settings from local file or VCAPS env var in the cloud
var config = require('./predix-config');

var json2xls = require('json2xls');
var fs =  require('fs');

var passport;  // only used if you have configured properties for UAA
// configure passport for oauth authentication with UAA
var passportConfig = require('./passport-config');

const uaa_util = require('predix-uaa-client');
var request = require('request');
var pretty = require('prettyjson');

var uaa_url = "https://a339a6af-44a5-4f87-ada2-cc6c49124765.predix-uaa.run.aws-usw02-pr.ice.predix.io/oauth/token?grant_type=client_credentials"
var client_id = "abhay"
var client_secret = "traffic_uaa"

// Call with client credentials (UAAUrl, ClientID, ClientSecret),
// will fetch a client token using these credentials.
// In this case the client needs authorized_grant_types: client_credentials

// if running locally, we need to set up the proxy from local config file:
var node_env = process.env.node_env || 'development';
if (node_env === 'development') {
  var devConfig = require('./localConfig.json')[node_env];
	proxy.setServiceConfig(config.buildVcapObjectFromLocalConfig(devConfig));
	proxy.setUaaConfig(devConfig);
}

//a back-end java microservice used in the Build A Basic App learningpath
var windServiceURL = devConfig ? devConfig.windServiceURL : process.env.windServiceURL;

console.log('************'+node_env+'******************');

if (config.isUaaConfigured()) {
	passport = passportConfig.configurePassportStrategy(config);
}

//turns on or off text or links depending on which tutorial you are in, guides you to the next tutorial
var learningpaths = require('./learningpaths/learningpaths.js');

/**********************************************************************
       SETTING UP EXRESS SERVER
***********************************************************************/
var app = express();

app.set('trust proxy', 1);
app.use(cookieParser('predixsample'));
// Initializing default session store
// *** Use this in-memory session store for development only. Use redis for prod. **
app.use(session({
	secret: 'predixsample',
	name: 'cookie_name',
	proxy: true,
	resave: true,
	saveUninitialized: true}));

if (config.isUaaConfigured()) {
	app.use(passport.initialize());
  // Also use passport.session() middleware, to support persistent login sessions (recommended).
	app.use(passport.session());
}

//Initializing application modules
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

var server = app.listen(process.env.VCAP_APP_PORT || 5000, function () {
	console.log ('Server started on port: ' + server.address().port);
});

/*******************************************************
SET UP MOCK API ROUTES
*******************************************************/
// Import route modules
// var viewServiceRoutes = require('./routes/view-service-routes.js')();
// var assetRoutes = require('./routes/predix-asset-routes.js')();
// var timeSeriesRoutes = require('./routes/time-series-routes.js')();

// add mock API routes.  (Remove these before deploying to production.)
//app.use('/api/view-service', jsonServer.router(viewServiceRoutes));
//app.use('/api/predix-asset', jsonServer.router(assetRoutes));
//app.use('/api/time-series', jsonServer.router(timeSeriesRoutes));

/****************************************************************************
	SET UP EXPRESS ROUTES
*****************************************************************************/

//route to retrieve learningpath info which drives what is displayed
app.get('/learning-paths', function(req, res) {
	//console.log(learningpaths);
	res.json({"learningPathsConfig": learningpaths.getLearningPaths(config)});
});

app.use(express.static(path.join(__dirname, process.env['base-dir'] ? process.env['base-dir'] : '../public')));

if (config.isUaaConfigured()) {
	//Use this route to make the entire app secure.  This forces login for any path in the entire app.
	app.use('/', index);
  //login route redirect to predix uaa login page
  app.get('/login',passport.authenticate('predix', {'scope': ''}), function(req, res) {
    // The request will be redirected to Predix for authentication, so this
    // function will not be called.
  });

  // access real Predix services using this route.
  // the proxy will add UAA token and Predix Zone ID.
  app.use('/predix-api',
  	passport.authenticate('main', {
  		noredirect: true
  	}),
  	proxy.router);

  //callback route redirects to secure route after login
  app.get('/callback', passport.authenticate('predix', {
  	failureRedirect: '/'
  }), function(req, res) {
  	console.log('Redirecting to secure route...');
  	res.redirect('/secure');
    });

  // example of calling a custom microservice.
  if (windServiceURL && windServiceURL.indexOf('https') === 0) {
    app.get('/api/services/windservices/*', passport.authenticate('main', { noredirect: true}),
      // if calling a secure microservice, you can use this middleware to add a client token.
      // proxy.addClientTokenMiddleware,
      proxy.customProxyMiddleware('/api', windServiceURL)
    );
  }

  /**
  ** this endpoint is required by Timeseries.js, for winddata is switch
  **/
    app.get('/config-details', passport.authenticate('main', {
      noredirect: true //Don't redirect a user to the authentication page, just show an error
      }), function(req, res) {
      console.log('Accessing the secure route data');
      res.setHeader('Content-Type', 'application/json');
      var configuration = {};
      if(!windServiceURL) {
        configuration.connectToTimeseries = "true";
      }
      if(config.assetURL && config.assetZoneId) {
        configuration.isConnectedAssetEnabled = "true";
      }
      res.send(JSON.stringify(configuration));

    });

  //Or you can follow this pattern to create secure routes,
  // if only some portions of the app are secure.
  app.get('/secure', passport.authenticate('main', {
    noredirect: true //Don't redirect a user to the authentication page, just show an error
    }), function(req, res) {
    console.log('Accessing the secure route');
    // modify this to send a secure.html file if desired.
    res.sendFile(path.join(__dirname + '/../secure/secure.html'));
    //res.send('<h2>This is a sample secure route.</h2>');
  });



}

//logout route
app.get('/logout', function(req, res) {
	req.session.destroy();
	req.logout();
  passportConfig.reset(); //reset auth tokens
  res.redirect(config.uaaURL + '/logout?redirect=' + config.appURL);
});

app.get('/favicon.ico', function (req, res) {
	res.send('favicon.ico');
});

var flatten = require('flat');
var jsonfile = require('jsonfile');
var jsondump = 'jsondump.json';
var timestamp = new Date().getTime();

app.get('/trafficData', function(req,res){
  uaa_util.getToken(uaa_url, client_id, client_secret).then((newToken) => {
    // Use token.access_token as a Bearer token Authroization header
    // in calls to secured services.
    console.log(newToken.access_token);

    var options = {
      method: 'GET',
      url: 'https://ie-traffic.run.aws-usw02-pr.ice.predix.io/v1/assets/1000000026/events',
      qs: 
      { 
        'event-types': 'TFEVT',
        'start-ts': timestamp - 3600000*3,
        'end-ts': timestamp,
        size: '50' 
      },
      /*qs:
      { 'event-types': 'TFEVT',
        'start-ts': '1453766605577',
        'end-ts': '1453772603879',
        'size': '10',
        'page': '1' },*/
      headers:
      { //'postman-token': '37688865-2e17-4500-ec8d-ba80df59f3b3',
        //'cache-control': 'no-cache',
        "Authorization": 'Bearer ' + newToken.access_token,
        "Predix-Zone-Id": 'aa7c9b1d-2145-4f6b-be0b-176dc72ef85b',
      }
    };

    request(options, function (error, response, body) {
      if (error) throw new Error(error);
      //console.log(pretty.render(JSON.parse(body)));
      var jsoncontents = JSON.parse(body)["_embedded"];
      jsonfile.writeFile(jsondump,jsoncontents,function (err)
      {
        console.error(err);
      })
      //console.log(flatten(jsoncontents["_embedded"]["events"]));
      //console.log(JSON.parse())
      //console.log(pretty.render(jsoncontents["_embedded"].events));
      //var xls = json2xls(flatten(jsoncontents["_embedded"].events));
      //fs.writeFileSync('data.xlsx',xls,'binary');
      res.send(body);
      return;
    });

  }).catch((err) => {
    console.error('Error getting token', err);
    });
})

var divider = {
  left: 0,
  center: 1,
  right: 0
}

app.get('/left', function(req,res){
  divider.left = 1;
  divider.center = 0;
  divider.right = 0;
  res.status(200).end();
})

app.get('/center', function(req,res){
  divider.left = 0;
  divider.center = 1;
  divider.right = 0;
  res.status(200).end();
})

app.get('/right', function(req,res){
  divider.left = 0;
  divider.center = 0;
  divider.right = 1;
  res.status(200).end();  
})

app.get('/dividerStatus', function(req, res){
  
  if(divider.left === 1){
    res.send('left');
    return;
  }

  if(divider.center === 1){
    res.send('center');
    return;
  }

  if(divider.right === 1){
    res.send('right');
    return;
  }

})

// Sample route middleware to ensure user is authenticated.
//   Use this route middleware on any resource that needs to be protected.  If
//   the request is authenticated (typically via a persistent login session),
//   the request will proceed.  Otherwise, the user will be redirected to the
//   login page.
//currently not being used as we are using passport-oauth2-middleware to check if
//token has expired
/*
function ensureAuthenticated(req, res, next) {
    if(req.isAuthenticated()) {
        return next();
    }
    res.redirect('/');
}
*/

////// error handlers //////
// catch 404 and forward to error handler
app.use(function(err, req, res, next) {
  console.error(err.stack);
	var err = new Error('Not Found');
	err.status = 404;
	next(err);
});

// development error handler - prints stacktrace
if (node_env === 'development') {
	app.use(function(err, req, res, next) {
		if (!res.headersSent) {
			res.status(err.status || 500);
			res.send({
				message: err.message,
				error: err
			});
		}
	});
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
	if (!res.headersSent) {
		res.status(err.status || 500);
		res.send({
			message: err.message,
			error: {}
		});
	}
});

module.exports = app;